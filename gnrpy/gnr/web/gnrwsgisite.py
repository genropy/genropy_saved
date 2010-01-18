from gnr.core.gnrbag import Bag
from gnr.web.gnrresourceloader import ResourceLoader
from beaker.middleware import SessionMiddleware
from paste import fileapp, httpexceptions
from paste import request as paste_request
from paste.httpheaders import ETAG
from weberror.evalexception import EvalException
from webob import Request, Response
from gnr.web.gnrwebapp import GnrWsgiWebApp
import os
import glob
from time import time
from gnr.core.gnrlang import gnrImport, instanceMixin
from threading import RLock
import thread
import mimetypes
from gnr.core.gnrsys import expandpath
from gnr.web.gnrbaseclasses import BaseWebtool
import cPickle
import inspect
from gnr.core.gnrprinthandler import PrintHandler
mimetypes.init()
site_cache = {}
class GnrWebServerError(Exception):
    pass
    
class PrintHandlerError(Exception):
    pass

class memoize(object):
    class Node:
        __slots__ = ['key', 'value', 'older', 'newer']
        def __init__(self, key, value, older=None, newer=None):
            self.key = key
            self.value = value
            self.older = older
            self.newer = newer

    def __init__(self, capacity=30):#, keyfunc=lambda *args, **kwargs: cPickle.dumps((args, kwargs))):
        self.capacity = capacity
        #self.keyfunc = keyfunc
        global site_cache
        self.nodes = site_cache or {}
        self.reset()


    def reset(self):
        for node in self.nodes:
            del self.nodes[node]
        self.mru = self.Node(None, None)
        self.mru.older = self.mru.newer = self.mru
        self.nodes[self.mru.key] = self.mru
        self.count = 1
        self.hits = 0
        self.misses = 0
        
    
    def cached_call(self):
        def decore(func):
            def wrapper(*args,**kwargs):
                key = (((func.__name__,)+args[1:]), cPickle.dumps(kwargs))
                #key = self.keyfunc(*((func.__name__,)+args), **kwargs)
                if key in self.nodes:
                    node = self.nodes[key]
                else:
                    # We have an entry not in the cache
                    self.misses += 1

                    value = func(*args, **kwargs)

                    lru = self.mru.newer  # Always true

                    # If we haven't reached capacity
                    if self.count < self.capacity:
                        # Put it between the MRU and LRU - it'll be the new MRU
                        node = self.Node(key, value, self.mru, lru)
                        self.mru.newer = node

                        lru.older = node
                        self.mru = node
                        self.count += 1
                    else:
                        # It's FULL! We'll make the LRU be the new MRU, but replace its
                        # value first
                        del self.nodes[lru.key]  # This mapping is now invalid
                        lru.key = key
                        lru.value = value
                        self.mru = lru

                    # Add the new mapping
                    self.nodes[key] = self.mru
                    return value

                # We have an entry in the cache
                self.hits += 1

                # If it's already the MRU, do nothing
                if node is self.mru:
                    return node.value

                lru = self.mru.newer  # Always true

                # If it's the LRU, update the MRU to be it
                if node is lru:
                    self.mru = lru
                    return node.value

                # Remove the node from the list
                node.older.newer = node.newer
                node.newer.older = node.older

                # Put it between MRU and LRU
                node.older = self.mru
                self.mru.newer = node

                node.newer = lru
                lru.older = node

                self.mru = node
                return node.value
            return wrapper
        return decore
        

cache = memoize()

class GnrWsgiSite(object):
    
    #cache = memoize()
    
    def log_print(self,str):
        if getattr(self,'debug',True):
            print str
    
    def __call__(self, environ, start_response):
        return self.wsgiapp(environ, start_response)
    
    def __init__(self, script_path, site_name=None, _config=None, _gnrconfig=None, counter=None, noclean=None,options=None):
        counter = int(counter or '0')
        self._currentPages={}
        self.site_path = os.path.dirname(os.path.abspath(script_path))
        self.site_name = site_name or os.path.basename(self.site_path)
        if _gnrconfig:
            self.gnr_config = _gnrconfig
        else:
            self.gnr_config = self.load_gnr_config()
            self.set_environment()
            
        if _config:
            self.config = _config
        else:
            self.config = self.load_site_config()
        
        self.home_uri = self.config['wsgi?home_uri'] or '/'
        self.session_type = self.config['wsgi?session_type'] or 'file'
        if self.home_uri[-1]!='/':
            self.home_uri+='/'
        self.mainpackage = self.config['wsgi?mainpackage']
        self.homepage = self.config['wsgi?homepage'] or self.home_uri+'index'
        self.indexpage = self.config['wsgi?homepage'] or '/index'
        if not self.homepage.startswith('/'):
            self.homepage = '%s%s'%(self.home_uri,self.homepage)
        self.secret = self.config['wsgi?secret'] or 'supersecret'
        self.config['secret'] = self.secret
        self.session_key = self.config['wsgi?session_key'] or 'gnrsession'
        self.debug = options and getattr(options,'debug',False)
        self.cache_max_age = self.config['wsgi?cache_max_age'] or 2592000
        self.gnrapp = self.build_gnrapp()
        self.wsgiapp = self.build_wsgiapp()
        self.db=self.gnrapp.db
        self.resource_loader = ResourceLoader(self)
        self.pages_dir = os.path.join(self.site_path, 'pages')
        self.site_static_dir = self.config['resources?site'] or '.'
        if self.site_static_dir and not os.path.isabs(self.site_static_dir):
            self.site_static_dir = os.path.normpath(os.path.join(self.site_path,self.site_static_dir))
        self.find_resources()
        self.find_gnrjs_and_dojo()
        self.page_factory_lock=RLock()
        self.webtools = self.find_webtools()
        self.print_handler=PrintHandler(parent = self)
        if counter==0 and self.debug:
            self.onInited(clean = not noclean)
        
    def _get_automap(self):
        return self.resource_loader.automap
    automap = property(_get_automap)
    def onInited(self, clean):
        if clean:
            self.dropAllConnectionFolders()
            self.initializePackages()
        else:
            pass
    def initializePackages(self):
        for pkg in self.gnrapp.packages.values():
            if hasattr(pkg,'onSiteInited'):
                pkg.onSiteInited()
                
    def dropAllConnectionFolders(self):
        connectionFolder=os.path.join(self.site_path, 'data', '_connections')
        for root, dirs, files in os.walk(connectionFolder, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        
        
    def find_webtools(self):
        def isgnrwebtool(cls):
            return inspect.isclass(cls) and issubclass(cls,BaseWebtool)
        tools = {}
        if 'webtools' in self.gnr_config['gnr.environment_xml']:
            for path in self.gnr_config['gnr.environment_xml'].digest('webtools:#a.path'):
                path = expandpath(path)
                if os.path.isdir(path):
                    for tool_module in os.listdir(path):
                        if tool_module.endswith('.py'):
                            module_path =os.path.join(path,tool_module)
                            try:
                                module = gnrImport(module_path,avoidDup=True)
                                tool_classes = inspect.getmembers(module, isgnrwebtool)
                                tool_classes = [(name.lower(),value) for name,value in tool_classes]
                                tools.update(dict(tool_classes))
                            except:
                                pass
        return tools
        
    
    def resource_name_to_path(self,res_id, safe=True):
        project_resource_path = os.path.join(self.site_path, '..','..','resources',res_id)
        if os.path.isdir(project_resource_path):
            return project_resource_path
        if 'resources' in self.gnr_config['gnr.environment_xml']:
            for path in self.gnr_config['gnr.environment_xml'].digest('resources:#a.path'):
                res_path=expandpath(os.path.join(path,res_id))
                if os.path.isdir(res_path):
                    return res_path
        if safe:
            raise Exception('Error: resource %s not found' % res_id)
    
    def find_gnrjs_and_dojo(self):
        self.dojo_path={}
        self.gnr_path={}
        for lib, path, cdn in self.gnr_config['gnr.environment_xml.static'].digest('js:#k,#a.path,#a.cdn'):
            if lib.startswith('dojo_'):
                self.dojo_path[lib[5:]] = path
            elif lib.startswith('gnr_'):
                self.gnr_path[lib[4:]] = path
    
    def find_resources(self):
        self.resources=Bag()
        resources_list = [(resource.label,resource.attr.get('path')) for resource in self.config['resources'] or []]
        for label,rsrc_path in resources_list:
            if rsrc_path:
                self.resources[label] = rsrc_path
            else:
                rsrc_path = self.resource_name_to_path(label)
                self.resources[label] = rsrc_path
        auto_resource_path = self.resource_name_to_path(self.site_name, safe=False)
        if auto_resource_path:
            self.resources[self.site_name] = os.path.realpath(auto_resource_path)
        self.resources_dirs = self.resources.values()
        self.resources_dirs.reverse()
        
    def set_environment(self):
        for var,value in self.gnr_config['gnr.environment_xml'].digest('environment:#k,#a.value'):
            var=var.upper()
            if not os.getenv(var):
                os.environ[var]=str(value)
    
    def load_gnr_config(self):
        config_path = expandpath('~/.gnr')
        if os.path.isdir(config_path):
            return Bag(config_path)
        config_path = expandpath(os.path.join('/etc/gnr'))
        if os.path.isdir(config_path):
            return Bag(config_path)
        return Bag()
    
    def load_site_config(self):
        site_config_path = os.path.join(self.site_path,'siteconfig.xml')
        site_config = self.gnr_config['gnr.siteconfig.default_xml']
        path_list=[]
        if 'projects' in self.gnr_config['gnr.environment_xml']:
            projects = [(expandpath(path),site_template) for path,site_template in self.gnr_config['gnr.environment_xml.projects'].digest('#a.path,#a.site_template') if os.path.isdir(expandpath(path))]
            for project_path,site_template in projects:
                sites=glob.glob(os.path.join(project_path,'*/sites'))
                path_list.extend([(site_path,site_template) for site_path in sites])
            for path,site_template in path_list:
                if path == os.path.dirname(self.site_path):
                    if site_config:
                        site_config.update(self.gnr_config['gnr.siteconfig.%s_xml'%site_template] or Bag())
                    else:
                        site_config = self.gnr_config['gnr.siteconfig.%s_xml'%site_template]
        if site_config:
            site_config.update(Bag(site_config_path))
        else:
            site_config = Bag(site_config_path)
        return site_config

    def _get_sitemap(self):
        return self.page_server.sitemap
    sitemap = property(_get_sitemap)        
        
    def loadResource(self,pkg, *path):
        return self.resource_loader.loadResource(pkg,*path)
    
    def get_path_list(self,path_info):
        # No path -> indexpage is served
        if path_info=='/' or path_info=='':
            path_info = self.indexpage
        if path_info.endswith('.py'):
            path_info = path_info[:-3]
        path_list = path_info.strip('/').split('/')
        path_list = [p for p in path_list if p]
        # if url starts with _ go to static file handling
        return path_list
        
    def dispatcher(self,environ,start_response):
        """Main WSGI dispatcher, calls serve_staticfile for static files and self.createWebpage for
         GnrWebPages"""
        t=time()
        request = Request(environ)
        response = Response()
        self.external_host = self.config['wsgi?external_host'] or request.host_url
        # Url parsing start
        path_list = self.get_path_list(request.path_info)
        request_kwargs=dict(request.params)
        if path_list[0].startswith('_tools'):
            return self.serve_tool(path_list,environ,start_response,**request_kwargs)
        elif path_list[0].startswith('_'):
            return self.serve_staticfile(path_list,environ,start_response,**request_kwargs)
        else:
            if self.debug:
                page = self.resource_loader(path_list, request, response)
            else:
                try:
                    page = self.resource_loader(path_list, request, response)
                except Exception,exc:
                    raise exc
            if not (page and page._call_handler):
                return self.not_found(environ,start_response)
            self.onServingPage(page)
            self.currentPage = page
            result = page()
            self.onServedPage(page)
            self.cleanup()
            self.setResultInResponse(result, response, totaltime = time()-t)
            return response(environ, start_response)
               
    def setResultInResponse(self, result, response, totaltime=None):
        if totaltime:
            response.headers['X-GnrTime'] = str(totaltime)
        if isinstance(result, unicode):
            response.content_type='text/plain'
            response.unicode_body=result
        elif isinstance(result, basestring):
            response.body=result
        elif isinstance(result, Response):
            response=result

    def onServingPage(self, page):
        pass
    
    def onServedPage(self, page):
        pass
    
    def cleanup(self):
        self.currentPage = None
        self.db.closeConnection()
        
    def serve_tool(self, path_list, environ, start_response, **kwargs):
        toolname = path_list[1]
        args = path_list[2:]
        tool = self.load_webtool(toolname)
        if not tool:
            return self.not_found(environ, start_response)
        response = Response()
        result = tool(*args, **kwargs)
        content_type = getattr(tool,'content_type')
        if content_type:
            response.content_type = content_type
        headers = getattr(tool,'headers',[])
        for header_name, header_value in headers:
            response.add_header(header_name, header_value)
        
        if isinstance(result, unicode):
            response.content_type='text/plain'
            response.unicode_body=result
        elif isinstance(result, basestring):
            response.body=result
        elif isinstance(result, Response):
            response=result
        return response(environ, start_response)
        
    def load_webtool(self, tool_name):
        webtool = self.webtools.get(tool_name)
        if webtool:
            return webtool()
    
    def not_found(self, environ, start_response, debug_message=None):
        exc = httpexceptions.HTTPNotFound(
            'The resource at %s could not be found'
            % paste_request.construct_url(environ),
            comment='SCRIPT_NAME=%r; PATH_INFO=%r; debug: %s'
            % (environ.get('SCRIPT_NAME'), environ.get('PATH_INFO'),
                debug_message or '(none)'))
        return exc.wsgi_application(environ, start_response)
        
    def build_wsgiapp(self):
        """Builds the wsgiapp callable wrapping self.dispatcher with WSGI middlewares """
        wsgiapp=self.dispatcher
        if self.debug:
            wsgiapp = EvalException(wsgiapp, debug=True)
        beaker_data_path = os.path.join(os.path.realpath(self.site_path),'data','_beaker_data')
        wsgiapp = SessionMiddleware(wsgiapp, config={'session.key':self.session_key, 'session.secret':self.secret, 
            'session.data_dir':beaker_data_path,
             'session.type':self.session_type, 'session.auto':True})
        #wsgiapp = Gzipper(wsgiapp, compresslevel=8)
        return wsgiapp
        
    def build_gnrapp(self):
        """Builds the GnrApp associated with this site"""
        instance_path = os.path.join(self.site_path,'instance')
        if not os.path.isdir(instance_path):
            instance_path = os.path.join(self.site_path,'..','..','instances',self.site_name)
        if not os.path.isdir(instance_path):
            instance_path = self.config['instance?path'] or self.config['instances.#0?path']
        app = GnrWsgiWebApp(instance_path, site=self)
        self.config.setItem('instances.app', app, path=instance_path)
        return app
        
    def onAutenticated  (self,avatar):
        if 'adm' in self.db.packages:
            self.db.packages['adm'].onAuthenticated(avatar)
              
    def pageLog(self,page,event):
        if 'adm' in page.db.packages:
            page.db.packages['adm'].pageLog(page,event)
            
    def connectionLog(self,page,event):
        if 'adm' in page.db.packages:
            page.db.packages['adm'].connectionLog(page,event)
    
    def getMessages(self,**kwargs):
        if 'sys' in self.gnrapp.db.packages:
            return self.gnrapp.db.table('sys.message').getMessages(**kwargs)
        
    def writeMessage(self,**kwargs):
        if 'sys' in self.gnrapp.db.packages:
            return self.gnrapp.db.table('sys.message').writeMessage(**kwargs)

    def deleteMessage(self,message_id):
        if 'sys' in self.gnrapp.db.packages:
            return self.gnrapp.db.table('sys.message').deleteMessage(message_id)
            
    def lockRecord(self,page,table,pkey):
        if 'sys' in self.gnrapp.db.packages:
            return self.gnrapp.db.table('sys.locked_record').lockRecord(page,table,pkey)
    def unlockRecord(self,page,table,pkey):
        if 'sys' in self.gnrapp.db.packages:
            return self.gnrapp.db.table('sys.locked_record').unlockRecord(page,table,pkey)
            
    def clearRecordLocks(self,**kwargs):
        if 'sys' in self.gnrapp.db.packages:
            return self.gnrapp.db.table('sys.locked_record').clearExistingLocks(**kwargs)
            
    def onClosePage(self):
        page=self.currentPage
        self.pageLog(page,'close')
        self.clearRecordLocks(page_id=page.page_id)
        self.db.commit()
        
    def debugger(self,debugtype,**kwargs):
        if self.currentPage:
            self.currentPage.debugger.output(debugtype,**kwargs)
            
    def notifyDbEvent(self,tblobj,record,event,old_record=None):
        if 'adm' in self.gnrapp.db.packages:
            page = self.currentPage
            if tblobj.attributes.get('broadcast') and page and page.subscribedTablesDict and tblobj.fullname in page.subscribedTablesDict:
                for page_id, connection_id in page.subscribedTablesDict[tblobj.fullname]:
                    self.setInClientPage(page_id=page_id,
                                        connection_id=connection_id,
                                        client_path='gnr.dbevent.%s'%tblobj.fullname.replace('.','_'),
                                        value=Bag([(k,v) for k,v in record.items() if not k.startswith('@')]),
                                        attributes=dict(dbevent=event))
    
    def setInClientPage(self, page_id=None, connection_id=None, client_path=None, value=None, attributes=None,  fired=False, saveSession=False):
        """@param save: remember to save on the last setInClientPage. The first call to setInClientPage implicitly lock the session util 
                        setInClientPage is called with save=True
        """
       
        currentPage = self.currentPage
        page_id = page_id or currentPage.page_id
        attributes = dict(attributes or {})
        attributes['_client_path'] = client_path    
        if not connection_id or  connection_id==currentPage.connection.connection_id and not currentPage.forked:
            currentPage.session.setInPageData('_clientDataChanges.%s' % client_path.replace('.','_'), 
                                        value, _attributes=attributes, page_id=page_id)
            if saveSession: 
                self.session.saveSessionData()
        else:
            msg_body = Bag()
            msg_body.setItem('dbevent', value,_client_data_path=client_path, dbevent=attributes['dbevent'])
            self.writeMessage(page_id=page_id,
                              body=msg_body,
                              message_type='datachange')
            
    
    def _get_currentPage(self):
        """property currentPage it returns the page currently used in this thread"""
        return self._currentPages.get(thread.get_ident())
        
    def _set_currentPage(self,page):
        """set currentPage for this thread"""
        self._currentPages[thread.get_ident()] = page
    currentPage = property(_get_currentPage,_set_currentPage)
        
    def callTableScript(self, page=None, table=None, respath=None, class_name=None, runKwargs=None,**kwargs):
        script=self.loadTableScript(page = page, table=table, respath=respath, class_name=class_name)
        if runKwargs:
            for k,v in runKwargs.items():
                kwargs[str(k)] = v
        #script.parentSite = self      idea
        return script(**kwargs)
        
    def loadTableScript(self, page, table, respath, class_name=None):
        class_name=class_name or 'Main'
        application=self.gnrapp
        if isinstance(table, basestring):
            table=application.db.table(table)
        modName = os.path.join('tables',table.name,*(respath.split('/')))
        resourceDirs = application.packages[table.pkg.name].resourceDirs
        modPathList = self.getResourceList(resourceDirs, modName, 'py') or []
        if modPathList:
            modPathList.reverse()
            basePath=modPathList.pop(0)
            resource_module = gnrImport(basePath, avoidDup=True)
            resource_class = getattr(resource_module,class_name,None)
            resource_obj = resource_class(page=page,resource_table=table)          
            for modPath in modPathList:
                resource_module = gnrImport(modPath, avoidDup=True)
                resource_class = getattr(resource_module,class_name,None)
                if resource_class:
                    instanceMixin(resource_obj,resource_class,only_callables=False)
            return resource_obj
        else:
            raise GnrWebServerError('Cannot import component %s' % modName)
        

    def getResourceList(self, resourceDirs, path ,ext=None):
        result=[]
        if ext and not path.endswith('.%s' % ext): path = '%s.%s' % (path, ext)
        for dpath in resourceDirs:
            fpath = os.path.join(dpath, path)
            if os.path.exists(fpath):
                result.append(fpath)
        return result
        
        

        
    def _get_siteResources(self):
        if not hasattr(self,'_siteResources'):
            self._siteResources=[]
            fpath = os.path.join(self.site_static_dir, '_resources')
            if os.path.isdir(fpath):
                self._siteResources.append(fpath) # we add a resource folder for common package
            resources_path = [fpath for fpath in self.resources_dirs if os.path.isdir(fpath)]
            #if os.path.isdir(fpath):
            self._siteResources.extend(resources_path) # we add a resource folder for common package
        return self._siteResources
    siteResources = property(_get_siteResources)
    # so we return a list of any possible resource folder starting from 
    # most customized and ending with most generic ones
    
    def pkg_page_url(self,pkg,*args):
        return ('%s%s/%s'%(self.home_uri,pkg,'/'.join(args))).replace('//','/')
    
    def webtools_url(self,tool,**kwargs):
        kwargs_string = '&'.join(['%s=%s'%(k,v) for k,v in kwargs.items()])
        return '%s%s_tools/%s?%s'%(self.external_host,self.home_uri,tool,kwargs_string)
        
    def site_static_path(self,*args):
        return os.path.join(self.site_static_dir, *args)

    def site_static_url(self,*args):
        return '%s_site/%s'%(self.home_uri,'/'.join(args))

    def pkg_static_path(self,pkg,*args):
        return os.path.join(self.gnrapp.packages[pkg].packageFolder, *args)

    def pkg_static_url(self,pkg,*args):
        return '%s_pkg/%s/%s'%(self.home_uri,pkg,'/'.join(args))
    
    def rsrc_static_path(self,rsrc,*args):
        return os.path.join(self.resources[rsrc], *args)
    
    def rsrc_static_url(self,rsrc,*args):
        return '%s_rsrc/%s/%s'%(self.home_uri,rsrc,'/'.join(args))
    
    def pages_static_path(self,*args):
        return os.path.join(self.site_path,'pages', *args)
    
    def pages_static_url(self,*args):
        return '%s_pages/%s'%(self.home_uri,'/'.join(args))
    
    def dojo_static_path(self, version,*args):
        return expandpath(os.path.join(self.dojo_path[version], *args))
    
    def dojo_static_url(self, version,*args):
        return '%s_dojo/%s/%s'%(self.home_uri,version,'/'.join(args))
    
    def gnr_static_path(self, version,*args):
        return expandpath(os.path.join(self.gnr_path[version], *args))

    def gnr_static_url(self, version,*args):
        return '%s_gnr/%s/%s'%(self.home_uri,version,'/'.join(args))
        
    def connection_static_path(self,connection_id,page_id,*args):
        return os.path.join(self.site_path,'data','_connections', connection_id, page_id, *args)
        
    def connection_static_url(self, page,*args):
        return '%s_conn/%s/%s/%s'%(self.home_uri,page.connection.connection_id, page.page_id,'/'.join(args))
    ########################### begin static file handling #################################
    
    def serve_staticfile(self,path_list,environ,start_response,download=False,**kwargs):
        handler = getattr(self,'static%s'%path_list[0],None)
        if handler:
            fullpath = handler(path_list)
            if fullpath and not os.path.isabs(fullpath):
                fullpath = os.path.normpath(os.path.join(self.site_path,fullpath))
        else:
            fullpath = None
        if not (fullpath and os.path.exists(fullpath)):
            return self.not_found(environ, start_response)
        if_none_match = environ.get('HTTP_IF_NONE_MATCH')
        if if_none_match:
            mytime = os.stat(fullpath).st_mtime
            if str(mytime) == if_none_match:
                headers = []
                ETAG.update(headers, mytime)
                start_response('304 Not Modified', headers)
                return [''] # empty body
        file_args=dict()
        if download:
            file_args['content_disposition']="attachment; filename=%s" % os.path.basename(fullpath)
        file_responder = fileapp.FileApp(fullpath,**file_args)
        if self.cache_max_age:
            file_responder.cache_control(max_age=self.cache_max_age)
        return file_responder(environ, start_response)
        
    
    def static_dojo(self,path_list):
        return self.dojo_static_path(*path_list[1:])
        
    def static_gnr(self,path_list):
        return self.gnr_static_path(*path_list[1:])
    
    def static_site(self,path_list):
        static_dir = self.config['resources?site'] or '.'
        return os.path.join(static_dir,*path_list[1:])
    
    def static_pages(self,path_list):
        static_dir = self.site_path
        return os.path.join(static_dir,'pages',*path_list[1:])
        
    def static_pkg(self,path_list):
        package_id = path_list[1]
        package = self.gnrapp.packages[package_id]
        if package:
            static_dir = package.packageFolder
            return os.path.join(static_dir,'webpages',*path_list[2:])
            
    def static_rsrc(self,path_list):
        resource_id = path_list[1]
        resource_path = self.resources.get(resource_id)
        if resource_path:
            return os.path.join(resource_path, *path_list[2:])
            
    def static_conn(self, path_list):
        connection_id, page_id = path_list[1],path_list[2]
        return self.connection_static_path(connection_id, page_id,*path_list[3:])
    ##################### end static file handling #################################
    
    def zipFiles(self, file_list=None, zipPath=None):
        import zipfile
        zipresult = open(zipPath,'wb')
        zip_archive = zipfile.ZipFile(zipresult, mode='w', compression=zipfile.ZIP_DEFLATED)
        for fname in file_list:
            zip_archive.write(fname, os.path.basename(fname))
        zip_archive.close()
        zipresult.close()
        
            
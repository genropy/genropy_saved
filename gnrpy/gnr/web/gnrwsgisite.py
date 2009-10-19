from gnr.core.gnrbag import Bag, DirectoryResolver
from gnr.core.gnrlang import gnrImport, getUuid, classMixin, cloneClass,instanceMixin
from gnr.core.gnrstring import splitAndStrip
from gnr.web.gnrwebpage import BaseResource
from gnr.web.gnrwsgipage import GnrWsgiPage
from gnr.web.gnrwebreqresp import GnrWebRequest,GnrWebResponse
#from gnr.web.gzipmiddleware import Gzipper
from beaker.middleware import SessionMiddleware
from paste import fileapp, httpexceptions, request
from paste.httpheaders import ETAG
from weberror.evalexception import EvalException
from webob import Request, Response
from gnr.web.gnrwebapp import GnrWsgiWebApp
import os
from time import time
from threading import RLock
import thread
import mimetypes
#import hashlib
from gnr.core.gnrsys import expandpath
from gnr.web.gnrbasewebtool import GnrBaseWebTool
import inspect
try:
    from gnr.core.gnrprinthandler import PrintHandler
    HAS_PRINTHANDLER = True
except:
    HAS_PRINTHANDLER = False
mimetypes.init()
class GnrWebServerError(Exception):
    pass
    
class PrintHandlerError(Exception):
    pass

class GnrWsgiSite(object):
    
    def __call__(self, environ, start_response):
        return self.wsgiapp(environ, start_response)
    
    def __init__(self, script_path, site_name=None, _config=None, _gnrconfig=None, counter=None, noclean=None):
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
        if self.home_uri[-1]!='/':
            self.home_uri+='/'
        self.mainpackage = self.config['wsgi?mainpackage']
        self.homepage = self.config['wsgi?homepage'] or self.home_uri+'index'
        if not self.homepage.startswith('/'):
            self.homepage = '%s/%s'%(self.home_uri,self.homepage)
        self.secret = self.config['wsgi?secret'] or 'supersecret'
        self.config['secret'] = self.secret
        self.session_key = self.config['wsgi?session_key'] or 'gnrsession'
        self.debug = self.config['wsgi?debug']=='true' or False
        self.cache_max_age = self.config['wsgi?cache_max_age'] or 2592000
        self.gnrapp = self.build_gnrapp()
        self.wsgiapp = self.build_wsgiapp()
        self.db=self.gnrapp.db
        self.build_automap()
        self.pages_dir = os.path.join(self.site_path, 'pages')
        self.site_static_dir = self.config['resources?site'] or '.'
        if self.site_static_dir and not os.path.isabs(self.site_static_dir):
            self.site_static_dir = os.path.normpath(os.path.join(self.site_path,self.site_static_dir))
        self.find_resources()
        self.find_gnrjs_and_dojo()
        self.page_factories={}
        self.page_factory_lock=RLock()
        self.webtools = self.find_webtools()
        if HAS_PRINTHANDLER:
            self.print_handler=PrintHandler(parent = self)
        else:
            self.print_handler=None
        if counter==0 and self.debug:
            self.onInited(clean = not noclean)
        
         
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
            return inspect.isclass(cls) and issubclass(cls,GnrBaseWebTool)
        tools = {}
        if 'webtools' in self.gnr_config['gnr.environment_xml']:
            for path in self.gnr_config['gnr.environment_xml'].digest('webtools:#a.path'):
                path = expandpath(path)
                if os.path.isdir(path):
                    for tool_module in os.listdir(path):
                        if tool_module.endswith('.py'):
                            module_path =os.path.join(path,tool_module)
                            module = gnrImport(module_path)
                            tool_classes = inspect.getmembers(module, isgnrwebtool)
                            tool_classes = [(name.lower(),value) for name,value in tool_classes]
                            tools.update(dict(tool_classes))
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
        resources_list = [(resource.label,resource.attr.get('path')) for resource in self.config['resources']]
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
        for path, site_template in self.gnr_config['gnr.environment_xml'].digest('sites:#a.path,#a.site_template'):
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
        if not hasattr(self,'_sitemap'):
            sitemap_path = os.path.join(self.site_path,'sitemap.xml')
            if not os.path.isfile(sitemap_path):
                sitemap_path = os.path.join(self.site_path,'automap.xml')
            _sitemap = Bag(sitemap_path)
            _sitemap.setBackRef()
            self._sitemap = _sitemap
        return self._sitemap
    sitemap = property(_get_sitemap)        
        
    def dispatcher(self,environ,start_response):
        """Main WSGI dispatcher, calls serve_staticfile for static files and self.createWebpage for
         GnrWebPages"""
        t=time()
        req = Request(environ)
        resp = Response()
        self.external_host = self.config['wsgi?external_host'] or req.host_url
        path_info = req.path_info
        if path_info==self.home_uri:
            path_info=self.homepage
        if path_info.endswith('.py'):
            path_info = path_info[:-3]
        path_list = path_info.strip('/').split('/')
        path_list = [p for p in path_list if p]
        # if url starts with _ go to static file handling
        page_kwargs=dict(req.params)
        if path_list[0].startswith('_tools'):
            return self.tools_call(path_list,environ,start_response,**page_kwargs)
        elif path_list[0].startswith('_'):
            return self.serve_staticfile(path_list,environ,start_response,**page_kwargs)
        # get the deepest node in the sitemap bag associated with the given url
        page_node,page_args=self.sitemap.getDeepestNode('.'.join(path_list))
        if self.mainpackage and not page_node: # try in the main package
            page_node,page_args=self.sitemap.getDeepestNode('.'.join([self.mainpackage]+path_list))
            
        if not page_node:
            return self.not_found(environ,start_response)
        page_attr = page_node.getInheritedAttributes()
        if not page_attr.get('path'):
            page_node,page_args=self.sitemap.getDeepestNode('.'.join(path_list+['index']))
        if not page_node:
            return self.not_found(environ,start_response)
        page_attr = page_node.getInheritedAttributes()
        if not page_attr.get('path'):
            return self.not_found(environ,start_response)
        if self.debug:
            page = self.page_create(**page_attr)
        else:
            try:
                page = self.page_create(**page_attr)
            except Exception,exc:
                raise exc
        #page.filepath = page_attr['path'] ### Non usare per favore...
        page.folders= page._get_folders()
        if '_rpc_resultPath' in page_kwargs:
            _rpc_resultPath=page_kwargs.pop('_rpc_resultPath')
        else:
            _rpc_resultPath=None
        if '_user_login' in page_kwargs:
            _user_login=page_kwargs.pop('_user_login')
        else:
            _user_login=None
        if 'page_id' in page_kwargs:
            page_id=page_kwargs.pop('page_id')
        else:
            page_id=None
        if 'debug' in page_kwargs:
            debug=page_kwargs.pop('debug')
        else:
            debug=None
        self.page_init(page,request=req, response=resp, page_id=page_id, debug=debug, 
                            _user_login=_user_login, _rpc_resultPath=_rpc_resultPath)
        if not page:
            return self.not_found(environ,start_response)
        page_method = page_args and page_args[0]
        if page_method and not 'method' in page_kwargs:
            page_kwargs['method'] = page_method
            page_args = page_args[1:]
        theme =page_kwargs.pop('theme',None) or getattr(page, 'theme', None) or self.config['dojo?theme'] or 'tundra'
        pagetemplate = getattr(page, 'pagetemplate', None) or self.config['dojo?pagetemplate'] # index
        result = page.index(theme=theme,pagetemplate=pagetemplate,**page_kwargs)
        if isinstance(result, unicode):
            resp.content_type='text/plain'
            resp.unicode_body=result
        elif isinstance(result, basestring):
            resp.body=result
        elif isinstance(result, Response):
            resp=result
        totaltime = time()-t
        resp.headers['X-GnrTime'] = str(totaltime)
        self.currentPage = None
        return resp(environ, start_response)
        
    def tools_call(self, path_list, environ, start_response, **kwargs):
        toolname = path_list[1]
        args = path_list[2:]
        tool = self.load_webtool(toolname)
        if not tool:
            return self.not_found(environ, start_response)
        response = Response()
        request = Request(environ)
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
            % request.construct_url(environ),
            comment='SCRIPT_NAME=%r; PATH_INFO=%r; debug: %s'
            % (environ.get('SCRIPT_NAME'), environ.get('PATH_INFO'),
                debug_message or '(none)'))
        return exc.wsgi_application(environ, start_response)
        
    def build_wsgiapp(self):
        """Builds the wsgiapp callable wrapping self.dispatcher with WSGI middlewares """
        wsgiapp=self.dispatcher
        if self.debug:
            wsgiapp = EvalException(wsgiapp, debug=True)
        beaker_path = os.path.join(os.path.realpath(self.site_path),'session_data')
        wsgiapp = SessionMiddleware(wsgiapp, dict(key=self.session_key, secret=self.secret, 
                data_dir=beaker_path, type='memory', auto=True))
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
        
    def find_instance(self,instance_name):
        if 'instances' in self.gnr_config['gnr.environment_xml']:
            path_list.extend([expandpath(path) for path in self.gnr_config['gnr.environment_xml'].digest('sites:#a.path') if os.path.isdir(expandpath(path))])
        
    
    def build_automap(self):
        def handleNode(node, pkg=None):
            attr = node.attr
            file_name = attr['file_name']
            node.attr = dict(
                name = '!!%s'%file_name.capitalize(),
                pkg = pkg
                )
            if attr['file_ext']=='py':
                node.attr['path']=attr['rel_path']
            node.label = file_name
            if node._value is None:
                node._value = ''
        self.automap=DirectoryResolver(os.path.join(self.site_path,'pages'),ext='py',include='*.py',exclude='_*,.*,*.pyc')()
        self.automap.walk(handleNode, _mode='', pkg='*')
        for package in self.gnrapp.packages.values():
            packagemap = DirectoryResolver(os.path.join(package.packageFolder, 'webpages'),
                                             include='*.py',exclude='_*,.*')()
            packagemap.walk(handleNode,_mode='',pkg=package.id)
            self.automap[package.id] = packagemap
        self.automap.toXml(os.path.join(self.site_path,'automap.xml'))
    
    def get_page_factory(self, path, pkg = None, rel_path=None):
        #if path in self.page_factories:
        #    return self.page_factories[path]
        page_module = gnrImport(path,importAs='%s-%s'%(pkg or 'site',str(path.lstrip('/').replace('/','_')[:-3])))
        page_factory = getattr(page_module,'page_factory',GnrWsgiPage)
        custom_class = getattr(page_module,'GnrCustomWebPage')
        py_requires = splitAndStrip(getattr(custom_class, 'py_requires', '') ,',')
        page_class = cloneClass('GnrCustomWebPage',page_factory)
        page_class.__module__ = page_module
        self.page_class_base_mixin(page_class, pkg=pkg)
        page_class.dojoversion = getattr(custom_class, 'dojoversion', None) or self.config['dojo?version'] or '11'
        page_class.theme = getattr(custom_class, 'theme', None) or self.config['dojo?theme'] or 'tundra'
        page_class.gnrjsversion = getattr(custom_class, 'gnrjsversion', None) or self.config['gnrjs?version'] or '11'
        page_class.maintable = getattr(custom_class, 'maintable', None)
        page_class.recordLock = getattr(custom_class, 'recordLock', None)
        page_class.polling = getattr(custom_class, 'polling', None)
        page_class.eagers = getattr(custom_class, 'eagers', {})
        page_class.css_requires = splitAndStrip(getattr(custom_class, 'css_requires', ''),',')
        page_class.js_requires = splitAndStrip(getattr(custom_class, 'js_requires', ''),',')
        page_class.pageOptions = getattr(custom_class,'pageOptions',{})
        page_class.auth_tags = getattr(custom_class, 'auth_tags', '')
        self.page_class_resourceDirs(page_class, path, pkg=pkg)
        self.page_pyrequires_mixin(page_class, py_requires)
        classMixin(page_class,custom_class)
        self.page_class_resourceDirs(page_class, path, pkg=pkg)
        page_class._packageId = pkg
        self.page_class_custom_mixin(page_class, rel_path, pkg=pkg)
        self.page_factories[path]=page_class
        return page_class

    def page_class_base_mixin(self,page_class,pkg=None):
        """Looks for custom classes in the package"""
        if pkg:
            package = self.gnrapp.packages[pkg]
        if package and package.webPageMixin:
            classMixin(page_class,package.webPageMixin) # first the package standard
        if self.gnrapp.webPageCustom:
            classMixin(page_class,self.gnrapp.webPageCustom) # then the application custom
        if package and package.webPageMixinCustom:
            classMixin(page_class,package.webPageMixinCustom) # finally the package custom

    
    def page_class_custom_mixin(self,page_class, path, pkg=None):
        """Look in the instance custom folder for a file named as the current webpage"""
        path=path.split(os.path.sep)
        if pkg:
            customPagePath=os.path.join(self.gnrapp.customFolder, pkg, 'webpages', *path)
            if os.path.isfile(customPagePath):
                component_page_module = gnrImport(customPagePath)
                component_page_class = getattr(component_page_module,'WebPage',None)
                if component_page_class:
                    classMixin(page_class, component_page_class)
                    
    def page_pyrequires_mixin(self, page_class, py_requires):
        for mix in py_requires:
            if mix:
                self.mixinResource(page_class, page_class._resourceDirs, mix)
                
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
        
    def notifyDbEvent_(self,tblobj,record,event,old_record=None):
        if 'adm' in self.gnrapp.db.packages:
            page = self.currentPage
            if tblobj.attributes.get('broadcast') and page and page.subscribedTablesDict and tblobj.fullname in page.subscribedTablesDict :
                msg_body = Bag()
                msg_body.setItem('dbevent', 
                                 Bag([(k,v) for k,v in record.items() if not k.startswith('@')]),
                                 _client_data_path='gnr.dbevent.%s'%tblobj.fullname.replace('.','_'), 
                                 dbevent=event)
                self.writeMessage(page_id=page.subscribedTablesDict[tblobj.fullname]['page_id'],
                                  body=msg_body,
                                  message_type='datachange')

    def notifyDbEvent(self,tblobj,record,event,old_record=None):
        if 'adm' in self.gnrapp.db.packages:
            print'***********notifyDbEvent*****************'
            page = self.currentPage
            if tblobj.attributes.get('broadcast') and page and page.subscribedTablesDict and tblobj.fullname in page.subscribedTablesDict:
                print'***********notifyDbEvent start for*****************'
                for page_id, connection_id in page.subscribedTablesDict[tblobj.fullname]:
                    print'***********notifyDbEvent setInClientPage*****************'
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
            print 'internal message'
            currentPage.session.setInPageData('_clientDataChanges.%s' % client_path.replace('.','_'), 
                                        value, _attributes=attributes, page_id=page_id)
            if saveSession: 
                self.session.saveSessionData()
        else:
            print 'external message'
            msg_body = Bag()
            msg_body.setItem('dbevent', value,_client_data_path=client_path, dbevent=attributes['dbevent'])
            print msg_body
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
    
    def loadResource(self,pkg, *path):
        resourceDirs = self.gnrapp.packages[pkg].resourceDirs
        resource_class = cloneClass('CustomResource',BaseResource)
        self.mixinResource(resource_class, resourceDirs, *path)
        resource_class.site = self
        return resource_class()
        
    def callTableScript(self, page=None, table=None, respath=None, class_name=None, **kwargs):
        script=self.loadTableScript(page = page, table=table, respath=respath, class_name=class_name)
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
            resource_module = gnrImport(basePath)
            resource_class = getattr(resource_module,class_name,None)
            resource_obj = resource_class(page=page,resource_table=table)          
            for modPath in modPathList:
                resource_module = gnrImport(modPath)
                resource_class = getattr(resource_module,class_name,None)
                if resource_class:
                    x=resource_class()
                    instanceMixin(resource_obj,x)
            return resource_obj
        else:
            raise GnrWebServerError('Cannot import component %s' % modName)
        
    def mixinResource(self, kls,resourceDirs,*path):
        path = os.path.join(*path)
        modName, clsName = path.split(':')
        modPathList = self.getResourceList(resourceDirs, modName, 'py') or []
        if modPathList:
            modPathList.reverse()
            for modPath in modPathList:
                component_module = gnrImport(modPath)
                component_class = getattr(component_module,clsName,None)
                if component_class:
                    classMixin(kls, component_class, site=self)
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
    def page_create(self,path=None,auth_tags=None,pkg=None,name=None):
        """Given a path returns a GnrWebPage ready to be called"""
        if pkg=='*':
            module_path = os.path.join(self.site_path,path)
            pkg = self.config['packages?default']
        else:
            module_path = os.path.join(self.gnrapp.packages[pkg].packageFolder,'webpages',path)
        try:
            self.page_factory_lock.acquire()
            page_class = self.get_page_factory(module_path, pkg = pkg, rel_path=path)
        finally:
            self.page_factory_lock.release()
        page = page_class(self, filepath = module_path, packageId = pkg)
        page.basename = path
        return page

    def page_init(self,page, request=None, response=None, page_id=None, debug=None, _user_login=None, _rpc_resultPath=None):
        self.currentPage=page
        page._rpc_resultPath=_rpc_resultPath
        page.forked=False
        page.siteFolder = page._sitepath=self.site_path
        page.folders= page._get_folders()
        page._request = request
        page.called_url = request.url
        page.path_url = request.path_url
        page.query_string = request.query_string
        page._user_login=_user_login
        if not response: 
            response = Response()
        page._response = response
        page.request = GnrWebRequest(request)
        page.response = GnrWebResponse(response)
        page.response.add_header('Pragma','no-cache')
        page.page_id = page_id or getUuid()
        page._htmlHeaders=[]
        page._cliCtxData = Bag()
        page.pagename = os.path.splitext(os.path.basename(page.filepath))[0].split(os.path.sep)[-1]
        page.pagepath = page.filepath.replace(page.folders['pages'], '')
        page.debug_mode = debug and True or False
        page._dbconnection=None
        
    def page_class_resourceDirs(self,page_class, path, pkg=None):  
        """Find a resource in current _resources folder or in parent folders one"""
        if pkg:
            pagesPath = os.path.join(self.gnrapp.packages[pkg].packageFolder , 'webpages')
        else:
            pagesPath = os.path.join(self.site_path,'pages')
        curdir = os.path.dirname(os.path.join(pagesPath,path))
        resourcePkg = None
        result = [] # result is now empty
        if pkg: # for index page or other pages at root level (out of any package)
            resourcePkg = self.gnrapp.packages[pkg].attributes.get('resourcePkg')
            fpath = os.path.join(self.site_path,'_custom', pkg, '_resources')
            if os.path.isdir(fpath):
                result.append(fpath) # we add a custom resource folder for current package
        fpath = os.path.join(self.site_path, '_resources')

        if os.path.isdir(fpath):
            result.append(fpath) # we add a custom resource folder for common package

        while curdir.startswith(pagesPath):
            fpath = os.path.join(curdir, '_resources')
            if os.path.isdir(fpath):
                result.append(fpath)
            curdir = os.path.dirname(curdir) # we add a resource folder for folder 
                                             # of current page
        if resourcePkg:
            for rp in resourcePkg.split(','):
                fpath = os.path.join(self.gnrapp.packages[rp].packageFolder , 'webpages', '_resources')
                if os.path.isdir(fpath):
                    result.append(fpath)
        #result.extend(self.siteResources)
        resources_list = self.resources_dirs
        result.extend(resources_list)
        page_class.tpldirectories=result+[self.gnr_static_path(page_class.gnrjsversion,'tpl')]
        page_class._resourceDirs = result

        
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
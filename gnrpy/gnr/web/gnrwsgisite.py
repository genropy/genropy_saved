from gnr.core.gnrbag import Bag

from paste import fileapp, httpexceptions
from paste import request as paste_request
from paste.httpheaders import ETAG
from weberror.evalexception import EvalException
from webob import Request, Response
from gnr.web.gnrwebapp import GnrWsgiWebApp
import os
import glob
import logging
from time import time
from gnr.core.gnrlang import gnrImport,boolean,deprecated
from gnr.core.gnrlang import GnrException
from threading import RLock
import thread
import mimetypes
from gnr.core.gnrsys import expandpath
import cPickle
import inspect
from gnr.core.gnrprinthandler import PrintHandler
from gnr.core.gnrmailhandler import MailHandler
from gnr.app.gnrdeploy import PathResolver
from gnr.web.gnrwsgisite_proxy.gnrresourceloader import ResourceLoader
from gnr.web.gnrwsgisite_proxy.gnrstatichandler import StaticHandlerManager

from gnr.web.gnrwsgisite_proxy.gnrshareddata import GnrSharedData_dict, GnrSharedData_memcache
from gnr.web.gnrwsgisite_proxy.gnrobjectregister import SiteRegister
import random
import shutil
mimetypes.init()
site_cache = {}

OP_TO_LOG={'x':'y'}

log = logging.getLogger('gnrwsgisite')

global GNRSITE
def currentSite():
    global GNRSITE
    return GNRSITE

class GnrSiteException(GnrException): 
    """Gnr Site Exception"""
    code='GNRSITE-001'
    description='!!Genro Site exception'
    caption="!! Site Error : %(message)s" 

class GnrWebServerError(Exception):
    pass
    
class PrintHandlerError(Exception):
    pass
    

class LockInfo():
    def __init__(self,val=False,**kwargs):
        self._status=val
        self.info=kwargs
    def __getattr__(self,attr):
        return getattr(self._status,attr)
        
class SiteLock(object):
    
    def __init__(self,site,locked_path, expiry=600):
        self.site=site
        self.locked_path=locked_path
        self.expiry=expiry or None

    def __enter__(self):
        return self.acquire()

    def __exit__(self, type, value, traceback):
        self.release()

    def acquire(self):
        page=self.site.currentPage
        lockinfo=dict(user=page.user,
                      page_id=page.page_id,
                      connection_id=page.connection_id,
                      currtime=time.time())
        
        result= self.site.shared_data.add(self.locked_path,lockinfo, expiry=self.expiry)
        if result:
            return LockInfo(True)
        else:
            info=self.site.shared_data.get(self.locked_path)
            return LockInfo(False,**info)

    
    def release(self):
        self.site.shared_data.delete(self.locked_path)

class memoize(object):
    class Node(object):
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
    def siteLock(self, **kwargs):
        return SiteLock(self, **kwargs)
    
    
    @property
    def shared_data(self):
        if not hasattr(self, '_shared_data'):
            memcache_config = self.config['memcache']
            if memcache_config:
                self._shared_data = GnrSharedData_memcache(self, memcache_config, debug=self.config.getAttr('memcache').get('debug'))
            else:
                self._shared_data = GnrSharedData_dict(self)
        return self._shared_data
        
    @property
    def guest_counter(self):
        self._guest_counter +=1
        return self._guest_counter
    
    def log_print(self,msg,code=None):
        if getattr(self,'debug',True):
            if code and code in OP_TO_LOG:
                print '***** %s : %s'%(code,msg)
            elif not code:
                print '***** OTHER : %s'%(msg)
    
    def __call__(self, environ, start_response):
        return self.wsgiapp(environ, start_response)
        

        
    def __init__(self, script_path, site_name=None, _config=None, _gnrconfig=None, counter=None, noclean=None,options=None):
        global GNRSITE
        GNRSITE = self
        counter = int(counter or '0')
        self._currentPages={}
        abs_script_path = os.path.abspath(script_path)
        if os.path.isfile(abs_script_path):
            self.site_path = os.path.dirname(abs_script_path)
        else:
            self.site_path=PathResolver().site_name_to_path(script_path)
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
        
        self.default_uri = self.config['wsgi?home_uri'] or '/'
        if self.default_uri[-1]!='/':
            self.default_uri+='/'
        self.mainpackage = self.config['wsgi?mainpackage']
        self.allConnectionsFolder = os.path.join(self.site_path, 'data', '_connections')
        self.allUsersFolder = os.path.join(self.site_path, 'data', '_users')

        self.homepage = self.config['wsgi?homepage'] or self.default_uri+'index'
        self.indexpage = self.config['wsgi?homepage'] or '/index'
        self._guest_counter = 0
        if not self.homepage.startswith('/'):
            self.homepage = '%s%s'%(self.default_uri,self.homepage)
        self.secret = self.config['wsgi?secret'] or 'supersecret'
        self.config['secret'] = self.secret
        self.debug = boolean(options and getattr(options,'debug',False) or self.config['wsgi?debug'])
        self.cache_max_age = self.config['wsgi?cache_max_age'] or 2592000
        self.statics=StaticHandlerManager(self)
        self.statics.addAllStatics()
        
        self.gnrapp = self.build_gnrapp()
        self.wsgiapp = self.build_wsgiapp()
        self.db=self.gnrapp.db
        self.dbstores=self.db.dbstores
        self.resource_loader = ResourceLoader(self)
        self.pages_dir = os.path.join(self.site_path, 'pages')
        self.site_static_dir = self.config['resources?site'] or '.'
        if self.site_static_dir and not os.path.isabs(self.site_static_dir):
            self.site_static_dir = os.path.normpath(os.path.join(self.site_path,self.site_static_dir))
        self.find_gnrjs_and_dojo()
        self.page_factory_lock=RLock()
        self.webtools = self.resource_loader.find_webtools()

        self.services = Bag()
        self.print_handler = self.addService('print',PrintHandler(self))
        self.mail_handler = self.addService('mail',MailHandler(self))
        self.register = SiteRegister(self)
        if counter==0 and self.debug:
            self.onInited(clean = not noclean)
            
    def addService(self,service_name,service_handler,**kwargs):
        self.services.setItem(service_name,service_handler,**kwargs)
        return service_handler
    
    def getService(self,service_name):
        return self.services[service_name]
    
    def addStatic(self, static_handler_factory, **kwargs):
        return self.statics.add(static_handler_factory, **kwargs)
    
    def getStaticPath(self,static,*args,**kwargs):
        autocreate = kwargs.get('autocreate',False)
        static_name,static_path = static.split(':')
        args=self.adaptStaticArgs(static_name, static_path, args)
        dest_dir= self.getStatic(static_name).path(*args)
        if autocreate and not os.path.exists(dest_dir):
            os.makedirs(dest_dir)
        return dest_dir


    def getStaticUrl(self,static,*args,**kwargs):
        nocache=kwargs.get('nocache')
        static_name,static_url = static.split(':')
        args=self.adaptStaticArgs(static_name,static_url, args)
        if nocache:
            return self.getStatic(static_name).nocache_url(*args)
        else:
            return self.getStatic(static_name).url(*args)

    def adaptStaticArgs(self,static_name, static_path,args):
        args=tuple(static_path.split('/'))+args
        if static_name=='user':
            args=(self.currentPage.user,)+args #comma does matter
        elif static_name=='conn':
            args=(self.currentPage.connection_id,self.currentPage.page_id)+args
        return args

    def getStatic(self,static_name):
        return self.statics.get(static_name)
    
    def exception(self,message):
        e= GnrSiteException(message=message)
        if self.currentPage:
            e.setLocalizer(self.currentPage.localizer)
        return e
        
        
   #def connFolderRemove(self, connection_id, rnd=True):        
   #    shutil.rmtree(os.path.join(self.allConnectionsFolder, connection_id),True)
   #    if rnd and random.random() > 0.9:
   #        live_connections=self.register_connection.connections()
   #        connection_to_remove=[connection_id for connection_id in os.listdir(self.allConnectionsFolder) if connection_id not in live_connections and os.path.isdir(connection_id)]
   #        for connection_id in connection_to_remove:
   #            self.connFolderRemove(connection_id, rnd=False)
   #    
    def _get_automap(self):
        return self.resource_loader.automap
    automap = property(_get_automap)
    
    def onInited(self, clean):
        if clean:
            self.dropConnectionFolder()
            self.initializePackages()
        else:
            pass
            
    def on_reloader_restart(self):
        self.shared_data.dump()
            
    def initializePackages(self):
        for pkg in self.gnrapp.packages.values():
            if hasattr(pkg,'onSiteInited'):
                pkg.onSiteInited()

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
        return self.resource_loader.sitemap
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
        
    def _get_home_uri(self):
        if self.currentPage.storename:
            return '%s%s/'%(self.default_uri,self.currentPage.storename)
        else:
            return self.default_uri
    home_uri=property(_get_home_uri)
    
    def parse_request_params(self, params):
        out_dict=dict()
        for name,value in params.items():
            if name.endswith('[]'):
                out_dict.setdefault(name[:-2],[]).append(value)
            else:
                out_dict[name]=value
        return out_dict
    
    def dispatcher(self,environ,start_response):
        """Main WSGI dispatcher, calls serve_staticfile for static files and self.createWebpage for
         GnrWebPages"""
        t=time()
        request = Request(environ)
        response = Response()
        self.external_host = self.config['wsgi?external_host'] or request.host_url
        # Url parsing start
        path_list = self.get_path_list(request.path_info)
        if path_list==['favicon.ico']:
            path_list=['_site','favicon.ico']
            self.log_print( '',code='FAVICON')
           # return response(environ, start_response)
    
        request_kwargs=self.parse_request_params(request.params)
        request_kwargs.pop('_no_cache_',None)
        storename = None
        #print 'site dispatcher: ',path_list
        
        if path_list[0] in self.dbstores:
            storename = path_list.pop(0)
        if path_list[0] == '_ping':
            self.log_print( 'kwargs: %s' % str(request_kwargs),code='PING')
            result=self.serve_ping(response,environ,start_response, **request_kwargs)
            if not isinstance(result,basestring):
                return result
            self.setResultInResponse(result, response, totaltime = time()-t)
            return response(environ, start_response)

        if path_list and path_list[0].startswith('_tools'):
            self.log_print( '%s : kwargs: %s' % (path_list,str(request_kwargs)),code='TOOLS')
            return self.serve_tool(path_list,environ,start_response,**request_kwargs)
        elif path_list and path_list[0].startswith('_'):
            self.log_print( '%s : kwargs: %s' % (path_list,str(request_kwargs)),code='STATIC')
            return self.statics.static_dispatcher(path_list,environ,start_response,**request_kwargs)
        else:
            self.log_print( '%s : kwargs: %s' % (path_list,str(request_kwargs)),code='RESOURCE')
            if self.debug:
                try:
                    page = self.resource_loader(path_list, request, response,environ=environ)
                except httpexceptions.HTTPException,exc:
                    return exc.wsgi_application(environ, start_response)
            else:
                try:
                    page = self.resource_loader(path_list, request, response)
                except httpexceptions.HTTPException,exc:
                    return exc.wsgi_application(environ, start_response)
                except Exception,exc:
                    log.exception("wsgisite.dispatcher: self.resource_loader failed with non-HTTP exception.")
                    log.exception(str(exc))
                    #raise exc # TODO: start_response will not be called if we get here, that could be the cause of some blank response errors.
            if not (page and page._call_handler):
                return self.not_found_exception(environ,start_response)
            self.onServingPage(page)
            self.currentPage = page
            page.storename = storename
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
            return self.not_found_exception(environ, start_response)
        tool.site=self
        response = Response()
        kwargs['environ']=environ
        kwargs['response']=response
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
    
    def not_found_exception(self, environ, start_response, debug_message=None):
        exc = httpexceptions.HTTPNotFound(
            'The resource at %s could not be found'
            % paste_request.construct_url(environ),
            comment='SCRIPT_NAME=%r; PATH_INFO=%r; debug: %s'
            % (environ.get('SCRIPT_NAME'), environ.get('PATH_INFO'),
                debug_message or '(none)'))
        return exc.wsgi_application(environ, start_response)
    
    def failed_exception(self, message,environ, start_response, debug_message=None):
        if '%%s' in message:
            message = message % paste_request.construct_url(environ)
        exc = httpexceptions.HTTPPreconditionFailed(message,
            comment='SCRIPT_NAME=%r; PATH_INFO=%r; debug: %s'
            % (environ.get('SCRIPT_NAME'), environ.get('PATH_INFO'),
                debug_message or '(none)'))
        return exc.wsgi_application(environ, start_response)
        
    def client_exception(self, message,environ):
        message = 'ERROR REASON : %s' % message
        exc = httpexceptions.HTTPClientError(message,
            comment='SCRIPT_NAME=%r; PATH_INFO=%r'
            % (environ.get('SCRIPT_NAME'), environ.get('PATH_INFO')))
        return exc
        
    def build_wsgiapp(self):
        """Builds the wsgiapp callable wrapping self.dispatcher with WSGI middlewares """
        wsgiapp=self.dispatcher
        if self.debug:
            wsgiapp = EvalException(wsgiapp, debug=True)
        return wsgiapp
        
    def build_gnrapp(self):
        """Builds the GnrApp associated with this site"""
        instance_path = os.path.join(self.site_path,'instance')
        if not os.path.isdir(instance_path):
            instance_path = os.path.join(self.site_path,'..','..','instances',self.site_name)
        if not os.path.isdir(instance_path):
            instance_path = self.config['instance?path'] or self.config['instances.#0?path']
        self.instance_path=instance_path
        app = GnrWsgiWebApp(instance_path, site=self)
        self.config.setItem('instances.app', app, path=instance_path)
        return app
        
    def onAuthenticated(self,avatar):
        if 'adm' in self.db.packages:
            self.db.packages['adm'].onAuthenticated(avatar)
        self.currentPage.btc.on_authenticated(avatar.user)
              
    def pageLog(self,event,page_id=None):
        if False and 'adm' in self.db.packages:
            self.db.table('adm.served_page').pageLog(event,page_id=page_id)
            
    def connectionLog(self,event,connection_id=None):
        if False and 'adm' in self.db.packages:
            self.db.table('adm.connection').connectionLog(event,connection_id=connection_id)

    def setPreference(self,path, data,pkg=''):
        if self.db.package('adm'):
            pkg=pkg or self.currentPage.packageId
            self.db.table('adm.preference').setPreference(path,data,pkg=pkg)
            
    def getPreference(self, path, pkg='', dflt=''):
        if self.db.package('adm'):
            pkg=pkg or self.currentPage.packageId
            return self.db.table('adm.preference').getPreference(path,pkg=pkg,dflt=dflt)
            
    def getUserPreference(self,path, pkg='',dflt='',username=''):
        if self.db.package('adm'):
            username = username or self.currentPage.user
            pkg=pkg or self.currentPage.packageId
            return self.db.table('adm.user').getPreference(path=path,pkg=pkg,dflt=dflt,username=username)
            
    def setUserPreference(self, path,data, pkg='',username=''):
        if self.db.package('adm'):
            pkg=pkg or self.currentPage.packageId
            username = username or self.currentPage.user
            self.db.table('adm.user').setPreference(path,data,pkg=pkg,username=username)
                    
    def dropConnectionFolder(self,connection_id=None):
        pathlist = ['data', '_connections']
        if connection_id:
            pathlist.append(connection_id)
        connectionFolder=os.path.join(self.site_path, *pathlist)
        for root, dirs, files in os.walk(connectionFolder, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        if connection_id:
            os.rmdir(connectionFolder)

    def lockRecord(self,page,table,pkey):
        if 'sys' in self.gnrapp.db.packages:
            return self.gnrapp.db.table('sys.locked_record').lockRecord(page,table,pkey)
            
    def unlockRecord(self,page,table,pkey):
        if 'sys' in self.gnrapp.db.packages:
            return self.gnrapp.db.table('sys.locked_record').unlockRecord(page,table,pkey)
            
    def clearRecordLocks(self,**kwargs):
        if 'sys' in self.gnrapp.db.packages:
            return self.gnrapp.db.table('sys.locked_record').clearExistingLocks(**kwargs)
            
    def onClosePage(self,page):
        page_id=page.page_id
        self.register.drop_page(page_id)
        self.pageLog('close',page_id=page_id)
        self.clearRecordLocks(page_id=page_id)
        
    def debugger(self,debugtype,**kwargs):
        """Send debug information to the client, if debugging is enabled.        
        Press Ctrl-Shift-B to open the debug pane in your browser.
        
        :param debugtype: string (values: 'sql' or 'py')
        """
        if self.currentPage:
            page = self.currentPage
            if self.debug or page.isDeveloper():
                page.debugger.output(debugtype,**kwargs)
        
    def notifyDbEvent(self,tblobj,record,event,old_record=None):
        if tblobj.attributes.get('broadcast'): 
            subscribers = self.register.pages(index_name=tblobj.fullname)
            value=Bag([(k,v) for k,v in record.items() if not k.startswith('@')])
            page = self.currentPage
            for page_id in subscribers.keys():
                page.setInClientData('gnr.dbevent.%s'%tblobj.fullname.replace('.','_'),value,
                                     attributes=dict(dbevent=event), page_id=page_id) 
                                   
    def sendMessageToClient(self,value,pageId=None,filters=None,origin=None,msg_path=None):
        """Send a message """
        from_page,from_user = (origin.page_id,origin.user) if origin else (None,'*Server*')
        self.currentPage.setInClientData(msg_path or 'gnr.servermsg', value,
                                       page_id=pageId,filters=filters,
                                      attributes=dict(from_user=from_user,from_page=from_page))
                            
    def _get_currentPage(self):
        """property currentPage it returns the page currently used in this thread"""
        return self._currentPages.get(thread.get_ident())
        
    def _set_currentPage(self,page):
        """set currentPage for this thread"""
        self._currentPages[thread.get_ident()] = page
    currentPage = property(_get_currentPage,_set_currentPage)
        
    def callTableScript(self, page=None, table=None, respath=None, class_name=None, runKwargs=None,**kwargs):
        """Call a script from a table's resources (i.e. ``_resources/tables/<table>/<respath>``).
        
        This is typically used to customize prints and batch jobs for a particular installation.
        
        see the method with the same name in webpage, :method:`gnr.web.gnrwebpage.GnrWebPage.callTableScript`
        """
        script=self.loadTableScript(page = page, table=table, respath=respath, class_name=class_name)
        if runKwargs:
            for k,v in runKwargs.items():
                kwargs[str(k)] = v
        result = script(**kwargs)
        return result
        
    def loadTableScript(self, page=None, table=None, respath=None, class_name=None):
        return self.resource_loader.loadTableScript( page=page, table=table, respath=respath, class_name=class_name)
  
    def _get_resources(self):
        if not hasattr (self,'_resources'):
            self._resources= self.resource_loader.site_resources()
        return self._resources
    resources=property(_get_resources)
    
    def _get_resources_dirs(self):
        if not hasattr (self,'_resources_dirs'):
            self._resources_dirs = self.resources.values()
            self._resources_dirs.reverse()
        return self._resources_dirs
    resources_dirs=property(_get_resources_dirs)
        
    def pkg_page_url(self,pkg,*args):
        return ('%s%s/%s'%(self.home_uri,pkg,'/'.join(args))).replace('//','/')
    
    def webtools_url(self,tool,**kwargs):
        kwargs_string = '&'.join(['%s=%s'%(k,v) for k,v in kwargs.items()])
        return '%s%s_tools/%s?%s'%(self.external_host,self.home_uri,tool,kwargs_string)
                
    def serve_ping(self,response,environ,start_response, page_id=None,reason=None,**kwargs):
        kwargs=self.parse_kwargs(kwargs)
        _lastUserEventTs=kwargs.get('_lastUserEventTs')
        page_item = self.register.refresh(page_id,_lastUserEventTs)
        if not page_item:
            return self.failed_exception('no longer existing page %s' %page_id,environ, start_response)

        
        self.handle_clientchanges(page_id,kwargs)
        envelope = Bag(dict(result=None))
        datachanges = self.get_datachanges(page_id,user=page_item['user'])
        if datachanges:
            envelope.setItem('dataChanges', datachanges)
        response.content_type = "text/xml"
        result = envelope.toXml(unresolved=True,  omitUnknownTypes=True)
        return result
    
    def get_datachanges(self,page_id,user=None,local_datachanges=None):
        result = Bag()
        local_datachanges = local_datachanges or []
        with self.register.pageStore(page_id) as pagestore:
            external_datachanges = list(pagestore.datachanges) or []
            subscriptions=pagestore.getItem('_subscriptions') or Bag()
            pagestore.reset_datachanges()
            store_datachanges=[]
            for storename,storesubscriptions in subscriptions.items():
                store = self.register.userStore(user) if storename =='user' else self.register.stores(storename)
                with store:
                    self._get_storechanges(store,storesubscriptions.items(),page_id,store_datachanges)
            
            for j,change in enumerate(external_datachanges+local_datachanges+store_datachanges):
                result.setItem('sc_%i' %j,change.value,change_path=change.path,change_reason=change.reason,
                                change_fired=change.fired,change_attr=change.attributes,
                                change_ts=change.change_ts,change_delete=change.delete)
        return result 
               
    def _get_storechanges(self,store, subscriptions, page_id, store_datachanges):
        datachanges=store.datachanges
        global_offsets=store.getItem('_subscriptions.offsets')
        if global_offsets is None:
            global_offsets = {}
            store.setItem('_subscriptions.offsets',global_offsets)
        for j,change in enumerate(datachanges):
            changepath =change.path 
            change_idx=change.change_idx
            for subpath,subdict in subscriptions :
                if subdict['on'] and changepath.startswith(subpath):
                    if change_idx >subdict.get('offset',0):
                        subdict['offset'] = change_idx
                        change.attributes = change.attributes or {}
                        if change_idx>global_offsets.get(subpath,0):
                            global_offsets[subpath] = change_idx
                            change.attributes['_new_datachange']=True
                        else:
                            change.attributes.pop('_new_datachange',None)
                        store_datachanges.append(change)
        return store_datachanges                      

    def handle_clientchanges(self,page_id=None,parameters=None):
        if '_serverstore_changes' in parameters:
            serverstore_changes = parameters.pop('_serverstore_changes',None)
            if serverstore_changes:
                with self.register.pageStore(page_id,triggered=False) as store:
                    if store:
                        for k,v in serverstore_changes.items():
                            store.setItem(k,v)
                
    def parse_kwargs(self,kwargs,workdate=None):
        catalog=self.gnrapp.catalog
        result = dict(kwargs)
        for k,v in kwargs.items():
            if isinstance(v, basestring):
                try:
                    v=catalog.fromTypedText(v)
                    if isinstance(v, basestring):
                        v = v.decode('utf-8')
                    result[k] = v
                except Exception, e:
                    raise e
        return result
 
 
 
 
    @deprecated
    def site_static_path(self,*args):
        return self.getStatic('site').path(*args)

    @deprecated
    def site_static_url(self,*args):
        return self.getStatic('site').url(*args)

   ########################### begin static file handling #################################
    ##################### end static file handling #################################
    
    def zipFiles(self, file_list=None, zipPath=None):
        import zipfile
        zipresult = open(zipPath,'wb')
        zip_archive = zipfile.ZipFile(zipresult, mode='w', compression=zipfile.ZIP_DEFLATED)
        for fname in file_list:
            zip_archive.write(fname, os.path.basename(fname))
        zip_archive.close()
        zipresult.close()
        
            
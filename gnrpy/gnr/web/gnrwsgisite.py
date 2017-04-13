from gnr.core.gnrbag import Bag
#from weberror.evalexception import EvalException
from backlash import DebuggedApplication

#from paste.exceptions.errormiddleware import ErrorMiddleware
#from weberror.errormiddleware import ErrorMiddleware
from webob import Request, Response
from webob.exc import WSGIHTTPException, HTTPNotFound, HTTPForbidden, HTTPPreconditionFailed, HTTPClientError
from gnr.web.gnrwebapp import GnrWsgiWebApp
from gnr.web.gnrwebpage import GnrUnsupportedBrowserException, GnrMaintenanceException
import os
import glob
import re
import logging
import subprocess
import urllib
import urllib2
import httplib2
import locale

from time import time
from collections import defaultdict
from gnr.core.gnrlang import deprecated,GnrException,tracebackBag
from gnr.core.gnrdecorator import public_method
from gnr.app.gnrconfig import getGnrConfig
from threading import RLock
import thread
import mimetypes
from gnr.core.gnrsys import expandpath
from gnr.core.gnrstring import boolean
from gnr.core.gnrdecorator import extract_kwargs

from gnr.core.gnrprinthandler import PrintHandler
from gnr.core.gnrtaskhandler import TaskHandler
from gnr.web.gnrwebreqresp import GnrWebRequest
from gnr.web.gnrwsgisite_proxy.gnrservicehandler import ServiceHandlerManager
from gnr.app.gnrdeploy import PathResolver
from gnr.web.services.gnrmail import WebMailHandler

from gnr.web.gnrwsgisite_proxy.gnrresourceloader import ResourceLoader
from gnr.web.gnrwsgisite_proxy.gnrstatichandler import StaticHandlerManager
from gnr.web.gnrwsgisite_proxy.gnrcommandhandler import CommandHandler

from gnr.web.gnrwsgisite_proxy.gnrsiteregister import SiteRegisterClient
from gnr.web.gnrwsgisite_proxy.gnrwebsockethandler import WsgiWebSocketHandler
import warnings

try:
    import uwsgi
    UWSGIMODE = True
except:
    UWSGIMODE = False
mimetypes.init()
site_cache = {}

OP_TO_LOG = {'x': 'y'}

IS_MOBILE = re.compile(r'iPhone|iPad|Android')

log = logging.getLogger(__name__)
warnings.simplefilter("default")
global GNRSITE


def currentSite():
    global GNRSITE
    return GNRSITE #JBE Why does this generate an error on Saving the doc == Undefined Name 'GNRSITE' ==?

class GnrSiteException(GnrException):
    """Standard Genro Site Exception
    
    * **code**: GNRSITE-001
    * **description**: Genro Site Exception
    """
    code = 'GNRSITE-001'
    description = '!!Genro Site exception'
    caption = "!! Site Error : %(message)s"
    
class GnrWebServerError(Exception):
    pass
    
class PrintHandlerError(Exception):
    pass
    
class UrlInfo(object):
    def __init__(self,site,url_list=None,request_kwargs=None): 
        self.site = site
        self.url_list = url_list
        self.request_args = None
        self.request_kwargs = request_kwargs or dict()
        self.relpath = None
        self.plugin = None
        path_list = list(url_list)
        if path_list[0]=='webpages':
            self.pkg = self.site.mainpackage
            self.basepath =  self.site.site_static_dir
        else:
            pkg_obj = self.site.gnrapp.packages[path_list[0]]
            if pkg_obj:
                path_list.pop(0)
            else:
                pkg_obj = self.site.gnrapp.packages[self.site.mainpackage]
            if path_list and path_list[0]=='_plugin':
                path_list.pop(0)
                self.plugin = path_list.pop(0)
                self.basepath= pkg_obj.plugins[self.plugin].webpages_path
            else:
                self.basepath =  os.path.join(pkg_obj.packageFolder,'webpages')
            self.pkg = pkg_obj.id
        if self.request_kwargs.pop('_mobile',False):
            mobilepath = os.path.join(self.basepath,'webpages_mobile')
            if os.path.exists(mobilepath):
                self.basepath = mobilepath
        currpath = []
        pathfile_cache = self.site.pathfile_cache
        path_list_copy = list(path_list)
        while path_list_copy:
            currpath.append(path_list_copy.pop(0))
            searchpath = os.path.splitext(os.path.join(self.basepath,*currpath))[0]
            cached_path = pathfile_cache.get(searchpath)
            if cached_path is None:
                cached_path = '%s.py' %searchpath
                if not os.path.isfile(cached_path):
                    cached_path = False
                pathfile_cache[searchpath] = cached_path
            if cached_path:
                self.relpath = cached_path
                self.request_args = path_list_copy
                return
        last_path = os.path.join(self.basepath,*path_list)
        last_index_path = os.path.join(last_path,'index.py')
        if os.path.isfile(last_index_path):
            pathfile_cache[last_path] = last_index_path
            pathfile_cache[last_index_path.replace('.py','')] = last_index_path
            self.relpath = last_index_path
            self.request_args = []
        else:
            self.request_args = path_list

#class SafeEvalException(EvalException):
#    def __call__(self, environ, start_response):
#        if not environ['wsgi.multiprocess']:
#            return super(SafeEvalException, self).__call__(environ, start_response)
#        else:
#            return self.application(environ, start_response)

class GnrWsgiSite(object):
    """TODO"""
    
    @property
    def guest_counter(self):
        """TODO"""
        self._guest_counter += 1
        return self._guest_counter
        
    def log_print(self, msg, code=None):
        """TODO
        
        :param msg: add??
        :param code: TODO"""
        if getattr(self, 'debug', True):
            if code and code in OP_TO_LOG:
                print '***** %s : %s' % (code, msg)
            elif not code:
                print '***** OTHER : %s' % (msg)

    def setDebugAttribute(self, options):
        self.force_debug = False
        if options:
            self.debug = boolean(options.debug)
            if self.debug:
                self.force_debug = True
        else:
            if self.config['wsgi?debug'] is not True and (self.config['wsgi?debug'] or '').lower()=='force':
                self.debug = True
                self.force_debug = True
            else:
                self.debug = boolean(self.config['wsgi?debug'])
            
                
    def __call__(self, environ, start_response):
        return self.wsgiapp(environ, start_response)
        
    def __init__(self, script_path, site_name=None, _config=None, _gnrconfig=None, counter=None, noclean=None,
                 options=None):
        global GNRSITE
        GNRSITE = self
        counter = int(counter or '0')
        self.pathfile_cache = {}
        self._currentPages = {}
        self._currentRequests = {}
        self._currentMaintenances = {}
        abs_script_path = os.path.abspath(script_path)
        self.remote_db = ''
        self._register = None
        if site_name and ':' in site_name:
            site_name,self.remote_db = site_name.split(':',1)
        if os.path.isfile(abs_script_path):
            self.site_path = os.path.dirname(abs_script_path)
        else:
            self.site_path = PathResolver().site_name_to_path(script_path)
        self.site_name = site_name or os.path.basename(self.site_path)
        site_parent=(os.path.dirname(self.site_path))
        if site_parent.endswith('sites'):
            self.project_name = os.path.basename(os.path.dirname(site_parent))
        else:
            self.project_name = None
        if _gnrconfig:
            self.gnr_config = _gnrconfig
        else:
            self.gnr_config = getGnrConfig(set_environment=True)
            
        self.config = self.load_site_config()
        self.cache_max_age = int(self.config['wsgi?cache_max_age'] or 5356800)
        self.default_uri = self.config['wsgi?home_uri'] or '/'
        if boolean(self.config['wsgi?static_import_psycopg']):
            try:
                import psycopg2
            except Exception:
                pass
        if self.default_uri[-1] != '/':
            self.default_uri += '/'
        self.mainpackage = self.config['wsgi?mainpackage']

        self.default_page = self.config['wsgi?default_page']
        self.root_static = self.config['wsgi?root_static']
        self.websockets= boolean(self.config['wsgi?websockets']) and UWSGIMODE
        self.allConnectionsFolder = os.path.join(self.site_path, 'data', '_connections')
        self.allUsersFolder = os.path.join(self.site_path, 'data', '_users')
        
        self.homepage = self.config['wsgi?homepage'] or self.default_uri + 'index'
        self.indexpage = self.config['wsgi?homepage'] or '/index'
        self._guest_counter = 0
        self._initExtraFeatures()
        if not self.homepage.startswith('/'):
            self.homepage = '%s%s' % (self.default_uri, self.homepage)
        self.secret = self.config['wsgi?secret'] or 'supersecret'
        self.config['secret'] = self.secret
        self.setDebugAttribute(options)
        #self.option_restore = options.restore if options else None
        #self.profile = boolean(options.profile) if options else boolean(self.config['wsgi?profile'])
        self.statics = StaticHandlerManager(self)
        self.statics.addAllStatics()
        self.compressedJsPath = None
        self.pages_dir = os.path.join(self.site_path, 'webpages')
        self.site_static_dir = self.config['resources?site'] or '.'
        if self.site_static_dir and not os.path.isabs(self.site_static_dir):
            self.site_static_dir = os.path.normpath(os.path.join(self.site_path, self.site_static_dir))
        self.find_gnrjs_and_dojo()
        self.gnrapp = self.build_gnrapp(options=options)
        default_locale = locale.getdefaultlocale()[0]
        self.server_locale = self.gnrapp.config('default?server_locale') or (locale.getdefaultlocale()[0].replace('_','-') if default_locale else 'en')
        self.wsgiapp = self.build_wsgiapp(options=options)
        self.db = self.gnrapp.db
        self.dbstores = self.db.dbstores
        self.connectionLogEnabled = self.db.package('adm') and boolean(self.config['options?connectionLog'])
        self.resource_loader = ResourceLoader(self)
        self.page_factory_lock = RLock()
        self.webtools = self.resource_loader.find_webtools()
        self.services = ServiceHandlerManager(self)
        self.print_handler = self.addService(PrintHandler, service_name='print')
        self.mail_handler = self.addService(WebMailHandler, service_name='mail')
        self.task_handler = self.addService(TaskHandler, service_name='task')
        self.process_cmd = CommandHandler(self)
        self.services.addSiteServices()
        
        self._remote_edit = options.remote_edit if options else None
        if counter == 0 and self.debug:
            self.onInited(clean=not noclean)
        if counter == 0 and options and options.source_instance:
            self.gnrapp.importFromSourceInstance(options.source_instance)
            self.db.commit()
            print 'End of import'

        cleanup = self.custom_config.getAttr('cleanup') or dict()
        self.cleanup_interval = int(cleanup.get('interval') or 120)
        self.page_max_age = int(cleanup.get('page_max_age') or 120)
        self.connection_max_age = int(cleanup.get('connection_max_age')or 600)

    @property
    def wsk(self):
        if not self.websockets:
            return
        if not hasattr(self,'_wsk'):
            self._wsk = WsgiWebSocketHandler(self)
        return self._wsk

    @property
    def register(self):
        if not self._register:
            self._register = SiteRegisterClient(self)
            self.checkPendingConnection()
        return self._register

    def getSubscribedTables(self,tables):
        if self._register:
            return self.register.filter_subscribed_tables(tables,register_name='page')

    @property
    def remote_edit(self):
        return self._remote_edit

    def _initExtraFeatures(self):
        self.extraFeatures = defaultdict(lambda:None)
        extra = self.config['extra']
        if extra:
            for n in extra:
                if n.label.startswith('wsk_') and not self.websockets:
                    #exclude wsk options if websockets are not activated
                    continue
                attr = dict(n.attr)
                if boolean(attr.pop('enabled',False)):
                    self.extraFeatures[n.label] = True
                    for k,v in attr.items():
                        self.extraFeatures['%s_%s' %(n.label,k)] = v

    def addService(self, service_handler, service_name=None, **kwargs):
        """TODO
        
        :param service_handler: TODO
        :param service_name: TODO"""
        return self.services.add(service_handler, service_name=service_name, **kwargs)
        
    def getService(self, service_name):
        """TODO
        
        :param service_name: TODO"""
        if self.currentPage and self.currentPage.rootenv:
            page = self.currentPage
            service_name = page.rootenv['custom_services.%s' %service_name] or service_name
        return self.services.get(service_name)
        
    def addStatic(self, static_handler_factory, **kwargs):
        """TODO
        
        :param service_handler_factory: TODO"""
        return self.statics.add(static_handler_factory, **kwargs)
        
    def getStaticPath(self, static, *args, **kwargs):
        """TODO
        
        :param static: TODO"""
        autocreate = kwargs.get('autocreate', False)
        if not ':' in static:
            return static
        static_name, static_path = static.split(':',1)
        args = self.adaptStaticArgs(static_name, static_path, args)
        dest_path = self.getStatic(static_name).path(*args)
        if autocreate:
            assert autocreate == True or autocreate < 0
            if autocreate != True:
                autocreate_args = args[:autocreate]
            else:
                autocreate_args = args
            dest_dir = self.getStatic(static_name).path(*autocreate_args)
            if not os.path.exists(dest_dir):
                os.makedirs(dest_dir)
        return dest_path


        
    def getStaticUrl(self, static, *args, **kwargs):
        """TODO
        
        :param static: TODO"""
        if not ':' in static:
            return static
        static_name, static_url = static.split(':',1)
        args = self.adaptStaticArgs(static_name, static_url, args)
        if kwargs:
            return self.getStatic(static_name).kwargs_url(*args, **kwargs)
        else:
            return self.getStatic(static_name).url(*args)

    def adaptStaticArgs(self, static_name, static_path, args):
        """TODO
        
        :param static_name: TODO
        :param static_path: TODO
        :param args: TODO"""
        args = tuple(static_path.split(os.path.sep)) + args
        if static_name == 'user':
            args = (self.currentPage.user,) + args #comma does matter
        elif static_name == 'conn':
            args = (self.currentPage.connection_id,) + args
        elif static_name == 'page':
            args = (self.currentPage.connection_id, self.currentPage.page_id) + args
        return args
        
    def getStatic(self, static_name):
        """TODO
        
        :param static_name: TODO"""
        return self.statics.get(static_name)
        
    def exception(self, message):
        """TODO
        
        :param message: TODO"""
        localizerKw=None
        if self.currentPage:
            localizerKw = self.currentPage.localizerKw
        return  GnrSiteException(message=message,localizerKw=localizerKw)
        
        #def connFolderRemove(self, connection_id, rnd=True):
        #    shutil.rmtree(os.path.join(self.allConnectionsFolder, connection_id),True)
        #    if rnd and random.random() > 0.9:
        #        live_connections=self.register_connection.connections()
        #        connection_to_remove=[connection_id for connection_id in os.listdir(self.allConnectionsFolder) if connection_id not in live_connections and os.path.isdir(connection_id)]
        #        for connection_id in connection_to_remove:
        #            self.connFolderRemove(connection_id, rnd=False)
        #

    def onInited(self, clean):
        """TODO
        
        :param clean: TODO"""
        if clean:
            self.dropConnectionFolder()
            self.initializePackages()
        else:
            pass


    def on_reloader_restart(self):
        """TODO"""
        pass
        #self.shared_data.dump()
        
    def initializePackages(self):
        """TODO"""
        self.gnrapp.pkgBroadcast('onSiteInited')
                
    def resource_name_to_path(self, res_id, safe=True):
        """TODO
        
        :param res_id: TODO
        :param safe: boolean. TODO"""
        project_resource_path = os.path.join(self.site_path, '..', '..', 'resources', res_id)
        if os.path.isdir(project_resource_path):
            return project_resource_path
        if 'resources' in self.gnr_config['gnr.environment_xml']:
            for path in self.gnr_config['gnr.environment_xml'].digest('resources:#a.path'):
                res_path = expandpath(os.path.join(path, res_id))
                if os.path.isdir(res_path):
                    return res_path
        if safe:
            raise Exception('Error: resource %s not found' % res_id)
         
         
    def getUrlInfo(self,path_list,request_kwargs=None,default_path=None):
        info = UrlInfo(self,path_list,request_kwargs)
        if not info.relpath and default_path:
            default_info = UrlInfo(self,default_path,request_kwargs)
            default_info.request_args = path_list
            return default_info
        return info
           
    def find_gnrjs_and_dojo(self):
        """TODO"""
        self.dojo_path = {}
        self.gnr_path = {}
        for lib, path, cdn in self.gnr_config['gnr.environment_xml.static'].digest('js:#k,#a.path,#a.cdn'):
            if lib.startswith('dojo_'):
                self.dojo_path[lib[5:]] = path
            elif lib.startswith('gnr_'):
                self.gnr_path[lib[4:]] = path
                
    def load_site_config(self):
        """TODO"""
        site_config_path = os.path.join(self.site_path, 'siteconfig.xml')
        site_config = self.gnr_config['gnr.siteconfig.default_xml']
        path_list = []
        if 'projects' in self.gnr_config['gnr.environment_xml']:
            projects = [(expandpath(path), site_template) for path, site_template in
                        self.gnr_config['gnr.environment_xml.projects'].digest('#a.path,#a.site_template') if
                        os.path.isdir(expandpath(path))]
            for project_path, site_template in projects:
                sites = glob.glob(os.path.join(project_path, '*/sites'))
                path_list.extend([(site_path, site_template) for site_path in sites])
            for path, site_template in path_list:
                if path == os.path.dirname(self.site_path):
                    if site_config:
                        site_config.update(self.gnr_config['gnr.siteconfig.%s_xml' % site_template] or Bag())
                    else:
                        site_config = self.gnr_config['gnr.siteconfig.%s_xml' % site_template]
        if site_config:
            site_config.update(Bag(site_config_path))
        else:
            site_config = Bag(site_config_path)
        return site_config

    @property
    def custom_config(self):
        if not getattr(self,'_custom_config',None):
            custom_config = Bag(self.config)
            preferenceConfig = self.getPreference(path='site_config',pkg='sys')
            if preferenceConfig is not None and preferenceConfig is not '':
                for pathlist,node in preferenceConfig.getIndex():
                    v = node.value
                    attr = node.attr
                    currnode = custom_config.getNode(pathlist,autocreate=True)
                    for k,v in attr.items():
                        if v not in ('',None):
                            currnode.attr[k] = v
                    if v and not isinstance(v,Bag):
                        currnode.value = v
            self._custom_config = custom_config
        return self._custom_config

    @property
    def locale(self):
        if self.currentPage:
            return self.currentPage.locale
        return self.site.server_locale

   #def _get_sitemap(self):
   #    return self.resource_loader.sitemap
   #    
   #sitemap = property(_get_sitemap)
    
    def getPackageFolder(self,pkg):
        return os.path.join(self.gnrapp.packages[pkg].packageFolder, 'webpages')

    def callExternalUrl(self,url,method=None,**kwargs):
        kwargs = kwargs or dict()
        for k in kwargs:
            kwargs[k] = self.gnrapp.catalog.asTypedText(kwargs[k])
        if method:
            url = '%s/%s' %(url,method)
        url= urllib2.urlopen(url,urllib.urlencode(kwargs))
        return url.read()

    def callGnrRpcUrl(self,url,method,*args,**kwargs):
        kwargs = kwargs or dict()
        for k in kwargs:
            kwargs[k] = self.gnrapp.catalog.asTypedText(kwargs[k])
        urlargs = [url,method]+list(args)
        url = '/'.join(urlargs)
        http = httplib2.Http()
        headers = {'Content-type': 'application/x-www-form-urlencoded'}
        response,content = http.request(url, 'POST', headers=headers, body=urllib.urlencode(kwargs))
        return self.gnrapp.catalog.fromTypedText(content)

    def writeException(self, exception=None, traceback=None):
        try:
            page = self.currentPage
            user, user_ip, user_agent = (page.user, page.user_ip, page.user_agent) if page else (None, None, None)
            return self.db.table('sys.error').writeException(description=str(exception),
                                                      traceback=traceback,
                                                      user=user,
                                                      user_ip=user_ip,
                                                      user_agent=user_agent)
        except Exception,writingErrorException:
            print '\n ####writingErrorException %s for exception %s' %(str(writingErrorException),str(exception))
        
    @public_method
    def writeError(self, description=None,error_type=None, **kwargs):
        try:
            page = self.currentPage
            user, user_ip, user_agent = (page.user, page.user_ip, page.user_agent) if page else (None, None, None)
            self.db.table('sys.error').writeError(description=description,error_type=error_type,user=user,user_ip=user_ip,user_agent=user_agent,**kwargs)
        except Exception,e:
            print str(e)
            pass

    def loadResource(self, pkg, *path):
        """TODO
        
        :param pkg: the :ref:`package <packages>` object
        :param \*path: TODO"""
        return self.resource_loader.loadResource(*path, pkg=pkg)
        
    def get_path_list(self, path_info):
        """TODO
        
        :param path_info: TODO"""
        # No path -> indexpage is served
        if path_info == '/' or path_info == '':
            path_info = self.indexpage
        if path_info.endswith('.py'):
            path_info = path_info[:-3]
        path_list = path_info.strip('/').split('/')
        path_list = [p for p in path_list if p]
        # if url starts with _ go to static file handling
        return path_list
        
    def _get_home_uri(self):
        if self.currentPage and self.currentPage.dbstore:
            return '%s%s/' % (self.default_uri, self.currentPage.dbstore)
        else:
            return self.default_uri
            
    home_uri = property(_get_home_uri)
        
    def parse_request_params(self, params):
        """TODO
        
        :param params: TODO"""
        out_dict = dict()
        for name in params.iterkeys():
            name = str(name)
            try:
                if name.endswith('[]'):
                    out_dict[name[:-2]]=params.getall(name)
                else:
                    out_dict[name] = params.getone(name)
            except UnicodeDecodeError:
                pass
        return out_dict
    
    @property
    def dummyPage(self):
        request = Request.blank('/sys/headless')
        response = Response()
        page = self.resource_loader(['sys', 'headless'], request, response)
        page.locale = self.server_locale
        return page
    
    @property
    def isInMaintenance(self):
        request = self.currentRequest
        request_kwargs = self.parse_kwargs(self.parse_request_params(request.params))
        path_list = self.get_path_list(request.path_info)
        first_segment = path_list[0] if path_list else ''
        if request_kwargs.get('forcedlogin') or (first_segment.startswith('_') and first_segment!='_ping'):
            return False
        elif 'page_id' in request_kwargs:
            self.currentMaintenance = 'maintenance' if self.register.pageInMaintenance(page_id=request_kwargs['page_id'],register_name='page') else None
            if not self.currentMaintenance or (first_segment == '_ping'):
                return False
            return True
        else:
            r = GnrWebRequest(request)
            c = r.get_cookie(self.site_name,'marshal', secret=self.config['secret'])
            user = c.value.get('user') if c else None
            return self.register.isInMaintenance(user)
            

    def dispatcher(self, environ, start_response):
        self.currentRequest = Request(environ)
        if self.isInMaintenance:
            return self.maintenanceDispatcher(environ, start_response)
        else:
            try:
                res = self._dispatcher(environ, start_response)
                #print res
                return res
            except self.register.errors.ConnectionClosedError:
                self.currentMaintenance = 'register_error'
                self._register = None
                return self.maintenanceDispatcher(environ, start_response)
            except Exception,e:
                page = self.currentPage
                if self.debug and ((page and page.isDeveloper()) or self.force_debug):
                    raise
                self.writeException(exception=e,traceback=tracebackBag())
                



    def maintenanceDispatcher(self,environ, start_response):
        request = self.currentRequest
        response = Response()
        request_kwargs = self.parse_kwargs(self.parse_request_params(request.params))
        path_list = self.get_path_list(request.path_info)
        if (path_list and path_list[0].startswith('_')) or ('method' in request_kwargs or 'rpc' in request_kwargs or '_plugin' in request_kwargs):
            response = self.setResultInResponse('maintenance', response, info_GnrSiteMaintenance=self.currentMaintenance)
            return response(environ, start_response)
        else:
            return self.serve_htmlPage('html_pages/maintenance.html', environ, start_response)
        

    def _dispatcher(self, environ, start_response):
        """Main :ref:`wsgi` dispatcher, calls serve_staticfile for static files and
        self.createWebpage for :ref:`gnrcustomwebpage`
        
        :param environ: TODO
        :param start_response: TODO"""
        self.currentPage = None
        t = time()
        request = self.currentRequest
        response = Response()
        self.external_host = self.config['wsgi?external_host'] or request.host_url
        # Url parsing start
        path_list = self.get_path_list(request.path_info)
        self.process_cmd.getPending()
        expiredConnections = self.register.cleanup()
        if expiredConnections:
            self.connectionLog('close',expiredConnections)
        if path_list == ['favicon.ico']:
            path_list = ['_site', 'favicon.ico']
            self.log_print('', code='FAVICON')
            # return response(environ, start_response)
        request_kwargs = self.parse_kwargs(self.parse_request_params(request.params))
        user_agent = request.user_agent or ''
        isMobile = len(IS_MOBILE.findall(user_agent))>0
        if isMobile:
            request_kwargs['_mobile'] = True
        request_kwargs.pop('_no_cache_', None)
        download_name = request_kwargs.pop('_download_name_', None)
        #print 'site dispatcher: ',path_list
        self.checkForDbStore(path_list,request_kwargs)
       #if path_list and (path_list[0] in self.dbstores):
       #    request_kwargs.setdefault('temp_dbstore',path_list.pop(0))
        if not path_list:
            path_list= self.get_path_list('')                   
        if path_list and path_list[0] == '_ping':
            try:
                self.log_print('kwargs: %s' % str(request_kwargs), code='PING')
                result = self.serve_ping(response, environ, start_response, **request_kwargs)
                if not isinstance(result, basestring):
                    return result
                response = self.setResultInResponse(result, response, info_GnrTime=time() - t,info_GnrSiteMaintenance=self.currentMaintenance)
                self.cleanup()
            except Exception,exc:
                raise 
            finally:
                self.cleanup()
            return response(environ, start_response)

        #static elements that doesn't have .py extension in self.root_static
        if  self.root_static and path_list and not path_list[0].startswith('_') and '.' in path_list[-1]:
            if path_list[-1].split('.')[-1]!='py':
                path_list = self.root_static.split('/')+path_list

        if path_list and path_list[0].startswith('_tools'):
            self.log_print('%s : kwargs: %s' % (path_list, str(request_kwargs)), code='TOOLS')
            return self.serve_tool(path_list, environ, start_response, **request_kwargs)
        elif path_list and path_list[0].startswith('_'):
            self.log_print('%s : kwargs: %s' % (path_list, str(request_kwargs)), code='STATIC')
            try:
                return self.statics.static_dispatcher(path_list, environ, start_response, **request_kwargs)
            except Exception, exc:
                return self.not_found_exception(environ,start_response)
        else:
            self.log_print('%s : kwargs: %s' % (path_list, str(request_kwargs)), code='RESOURCE')
            try:
                page = self.resource_loader(path_list, request, response, environ=environ,request_kwargs=request_kwargs)
                if page:
                    page.download_name = download_name
            except WSGIHTTPException, exc:
                return exc(environ, start_response)
            except Exception, exc:
                log.exception("wsgisite.dispatcher: self.resource_loader failed with non-HTTP exception.")
                log.exception(str(exc))
                raise
            if not (page and page._call_handler):
                return self.not_found_exception(environ, start_response)
            self.currentPage = page
            self.onServingPage(page)
            try:
                result = page()
               
                if page.download_name:
                    download_name = unicode(page.download_name)
                    content_type = getattr(page,'forced_mimetype',None) or mimetypes.guess_type(download_name)[0]
                    if content_type:
                        page.response.content_type = content_type
                    page.response.add_header("Content-Disposition", str("attachment; filename=%s" %download_name))
                if isinstance(result, file):
                    return self.statics.fileserve(result, environ, start_response,nocache=True,download_name=page.download_name)
            except GnrUnsupportedBrowserException:
                return self.serve_htmlPage('html_pages/unsupported.html', environ, start_response)
            except GnrMaintenanceException:
                return self.serve_htmlPage('html_pages/maintenance.html', environ, start_response)
            finally:
                self.onServedPage(page)
                self.cleanup()
            response = self.setResultInResponse(result, response, info_GnrTime=time() - t,info_GnrSqlTime=page.sql_time,info_GnrSqlCount=page.sql_count,
                                                                info_GnrXMLTime=getattr(page,'xml_deltatime',None),info_GnrXMLSize=getattr(page,'xml_size',None),
                                                                info_GnrSiteMaintenance=self.currentMaintenance,
                                                                mimetype=getattr(page,'forced_mimetype',None))
            
            return response(environ, start_response)
            
    def serve_htmlPage(self, htmlPageName, environ, start_response):
        uri = self.dummyPage.getResourceUri(htmlPageName)
        if uri:
            path_list = uri[1:].split('/')
            return self.statics.static_dispatcher(path_list, environ, start_response,nocache=True)

    def checkForDbStore(self,path_list,request_kwargs):
        if not path_list and not (request_kwargs.get('temp_dbstore') or '').startswith('@'):
            return
        first = path_list[0]
        instanceNode = None
        if first.startswith('@'):
            instanceNode = self.gnrapp.config.getNode('aux_instances.%s' %first[1:])
        if first in self.dbstores or instanceNode:
            request_kwargs.setdefault('temp_dbstore',path_list.pop(0))
        temp_dbstore = request_kwargs.get('temp_dbstore')
        if temp_dbstore and temp_dbstore.startswith('@'):
            instance_name = temp_dbstore[1:]
            storename = 'instance_%s' %instance_name
            request_kwargs['temp_dbstore'] = storename
            if not storename in self.dbstores:
                auxapp = self.gnrapp.getAuxInstance(instance_name)
                if not auxapp:
                    raise Exception('not existing aux instance %s' %instance_name)
                dbattr = auxapp.config.getAttr('db')
                if auxapp.remote_db:
                    remote_db_attr = auxapp.config.getAttr('remote_db.%s' %auxapp.remote_db)
                    if remote_db_attr:
                        if 'ssh_host' in remote_db_attr:
                            host = remote_db_attr['ssh_host'].split('@')[1] if '@' in remote_db_attr['ssh_host'] else remote_db_attr['ssh_host']
                            port = remote_db_attr.get('port')
                            dbattr['remote_host'] = host
                            dbattr['remote_port'] = port
                self.db.stores_handler.add_store(storename,dbattr=dbattr)
        

    @extract_kwargs(info=True)
    def setResultInResponse(self, result, response,info_kwargs=None,**kwargs):
        """TODO
        
        :param result: TODO
        :param response: TODO
        :param totaltime: TODO"""
        for k,v in info_kwargs.items():
            if v is not None:
                response.headers['X-%s' %k] = str(v)
        if isinstance(result, unicode):
            response.content_type = kwargs.get('mimetype') or 'text/plain'
            response.unicode_body = result # PendingDeprecationWarning: .unicode_body is deprecated in favour of Response.text
        elif isinstance(result, basestring):
            response.body = result
        elif isinstance(result, Response):
            response = result
        elif callable(result):
            response = result
        return response
        
    def onServingPage(self, page):
        """TODO
        
        :param page: TODO"""
        pass
        
    def onServedPage(self, page):
        """TODO
        
        :param page: TODO"""
        pass
        
    def cleanup(self):
        """clean up"""
        debugger = getattr(self.currentPage,'debugger',None)
        if debugger:
            debugger.onClosePage()
        self.currentPage = None
        self.db.closeConnection()
        #self.shared_data.disconnect_all()
        
    def serve_tool(self, path_list, environ, start_response, **kwargs):
        """TODO
        
        :param path_list: TODO
        :param environ: TODO
        :param start_response: TODO"""
        toolname = path_list[1]
        args = path_list[2:]
        tool = self.load_webtool(toolname)
        if not tool:
            return self.not_found_exception(environ, start_response)
        tool.site = self
        response = Response()
        kwargs['environ'] = environ
        kwargs['response'] = response
        result = tool(*args, **kwargs)
        content_type = getattr(tool, 'content_type', None)
        if content_type:
            response.content_type = content_type
        headers = getattr(tool, 'headers', [])
        for header_name, header_value in headers:
            response.add_header(header_name, header_value)
            
        if isinstance(result, unicode):
            response.content_type = 'text/plain'
            response.unicode_body = result
        elif isinstance(result, basestring):
            response.body = result
        elif isinstance(result, Response):
            response = result
        return response(environ, start_response)
        
    def load_webtool(self, tool_name):
        """TODO
        
        :param tool_name: the tool name"""
        webtool = self.webtools.get(tool_name)
        if webtool:
            return webtool()
    
    def request_url(self,environ):
        return Request(environ).url       

    def not_found_exception(self, environ, start_response, debug_message=None):
        """TODO
        
        :param environ: TODO
        :param start_response: add??
        :param debug_message: TODO"""
        exc = HTTPNotFound(
                'The resource at %s could not be found'
                % self.request_url(environ),
                comment='SCRIPT_NAME=%r; PATH_INFO=%r; debug: %s'
                % (environ.get('SCRIPT_NAME'), environ.get('PATH_INFO'),
                   debug_message or '(none)'), )
        return exc(environ, start_response)
        
    def forbidden_exception(self, environ, start_response, debug_message=None):
        """TODO
        
        :param environ: TODO
        :param start_response: add??
        :param debug_message: TODO"""
        exc = HTTPForbidden(
                'The resource at %s could not be viewed'
                % self.request_url(environ),
                comment='SCRIPT_NAME=%r; PATH_INFO=%r; debug: %s'
                % (environ.get('SCRIPT_NAME'), environ.get('PATH_INFO'),
                   debug_message or '(none)'))
        return exc(environ, start_response)
        
    def failed_exception(self, message, environ, start_response, debug_message=None):
        """TODO
        
        :param message: TODO
        :param environ: TODO
        :param start_response: add??
        :param debug_message: TODO"""
        if '%%s' in message:
            message = message % self.request_url(environ)
        exc = HTTPPreconditionFailed(message,
                                                    comment='SCRIPT_NAME=%r; PATH_INFO=%r; debug: %s'
                                                    % (environ.get('SCRIPT_NAME'), environ.get('PATH_INFO'),
                                                       debug_message or '(none)'))
        return exc(environ, start_response)
        
    def client_exception(self, message, environ):
        """TODO
        
        :param message: TODO
        :param environ: TODO"""
        message = 'ERROR REASON : %s' % message
        exc = HTTPClientError(message,
                                             comment='SCRIPT_NAME=%r; PATH_INFO=%r'
                                             % (environ.get('SCRIPT_NAME'), environ.get('PATH_INFO')))
        return exc
        
    def build_wsgiapp(self, options=None):
        """Build the wsgiapp callable wrapping self.dispatcher with WSGI middlewares"""
        wsgiapp = self.dispatcher
        self.error_smtp_kwargs = None
        profile = boolean(options.profile) if options else boolean(self.config['wsgi?profile'])
        gzip = boolean(options.gzip) if options else boolean(self.config['wsgi?gzip'])
        if profile:
            try:
                from repoze.profile.profiler import AccumulatingProfileMiddleware
            except ImportError:
                AccumulatingProfileMiddleware = None
            if AccumulatingProfileMiddleware:
                wsgiapp = AccumulatingProfileMiddleware(
                   wsgiapp,
                   log_filename=os.path.join(self.site_path, 'site_profiler.log'),
                   cachegrind_filename=os.path.join(self.site_path, 'cachegrind_profiler.out'),
                   discard_first_request=True,
                   flush_at_shutdown=True,
                   path='/__profile__'
                  )

        if self.debug:
            #wsgiapp = SafeEvalException(wsgiapp, debug=True)
            wsgiapp = DebuggedApplication(wsgiapp)
        else:
            pass
            #err_kwargs = dict(debug=True)
            #if 'debug_email' in self.config:
            #    error_smtp_kwargs = self.config.getAttr('debug_email')
            #    if error_smtp_kwargs.get('smtp_password'):
            #        error_smtp_kwargs['smtp_password'] = error_smtp_kwargs['smtp_password'].encode('utf-8')
            #    if error_smtp_kwargs.get('smtp_username'):
            #        error_smtp_kwargs['smtp_username'] = error_smtp_kwargs['smtp_username'].encode('utf-8')
            #    if 'error_subject_prefix' not in error_smtp_kwargs:
            #        error_smtp_kwargs['error_subject_prefix'] = '[%s] ' % self.site_name
            #    error_smtp_kwargs['error_email'] = error_smtp_kwargs['error_email'].replace(';', ',').split(',')
            #    if 'smtp_use_tls' in error_smtp_kwargs:
            #        error_smtp_kwargs['smtp_use_tls'] = (error_smtp_kwargs['smtp_use_tls'] in (True, 'true', 't', 'True', '1', 'TRUE'))
            #    self.error_smtp_kwargs = dict(error_smtp_kwargs)
            #    self.error_smtp_kwargs['error_email_from'] = self.error_smtp_kwargs.pop('from_address')
            #    err_kwargs.update(error_smtp_kwargs)
            #wsgiapp = ErrorMiddleware(wsgiapp, **err_kwargs)
        if gzip:
            from paste.gzipper import middleware as gzipper_middleware
            wsgiapp = gzipper_middleware(wsgiapp)
        return wsgiapp
        
    def build_gnrapp(self, options=None):
        """Builds the GnrApp associated with this site"""
        instance_path = os.path.join(self.site_path, 'instance')
        if not os.path.isdir(instance_path):
            instance_path = os.path.join(self.site_path, '..', '..', 'instances', self.site_name)
        if not os.path.isdir(instance_path):
            instance_path = self.config['instance?path'] or self.config['instances.#0?path']
        self.instance_path = instance_path
        #restorepath = self.option_restore
        restorepath = options.restore if options else None
        restorefiles=[]
        if restorepath:
            if restorepath == 'auto':
                restorepath = self.getStaticPath('site:maintenance','restore',autocreate=True)
            restorefiles = [j for j in os.listdir(restorepath) if not j.startswith('.')]
            if restorefiles:
                restorepath = os.path.join(restorepath,restorefiles[0])
            else:
                restorepath = None
        if self.remote_db:
            instance_path = '%s@%s' %(instance_path,self.remote_db)
        app = GnrWsgiWebApp(instance_path, site=self,restorepath=restorepath)
        self.config.setItem('instances.app', app, path=instance_path)
        for f in restorefiles:
            if os.path.isfile(restorepath):
                os.rename(restorepath,self.getStaticPath('site:maintenance','restored',f,autocreate=-1))
        return app
        
    def onAuthenticated(self, avatar):
        """TODO
        
        :param avatar: the avatar (user that logs in)"""
        #if 'adm' in self.db.packages:
        #    self.db.packages['adm'].onAuthenticated(avatar)
        #pkgbroadcast?
        self.gnrapp.pkgBroadcast('onAuthenticated',avatar)
       #
       # for pkg in self.db.packages.values():
       #     if hasattr(pkg,'onAuthenticated'):
       #         pkg.onAuthenticated(avatar)
       # 

    def checkPendingConnection(self):
        if self.connectionLogEnabled:
            self.db.table('adm.connection').dropExpiredConnections()

    def pageLog(self, event, page_id=None):
        """TODO
        
        :param event: TODO
        :param page_id: the 22 characters page id"""
        if self.connectionLogEnabled:
            self.db.table('adm.served_page').pageLog(event, page_id=page_id)


    def connectionLog(self, event, connection_id=None):
        """TODO
        
        :param event: TODO
        :param connection_id: TODO"""
        if self.connectionLogEnabled:
            self.db.table('adm.connection').connectionLog(event, connection_id=connection_id)
            
    def setPreference(self, path, data, pkg=''):
        """TODO
        
        :param path: TODO
        :param data: TODO
        :param pkg: the :ref:`package <packages>` object"""
        if self.db.package('adm'):
            pkg = pkg or self.currentPage.packageId
            self.db.table('adm.preference').setPreference(path, data, pkg=pkg)
            
    def getPreference(self, path, pkg=None, dflt=None):
        """TODO
        
        :param path: TODO
        :param pkg: the :ref:`package <packages>` object
        :param dflt: TODO"""
        if self.db.package('adm'):
            pkg = pkg or self.currentPage.packageId
            return self.db.table('adm.preference').getPreference(path, pkg=pkg, dflt=dflt)
            
    def getUserPreference(self, path, pkg=None, dflt=None, username=None):
        """TODO
        
        :param path: TODO
        :param pkg: the :ref:`package <packages>` object
        :param dflt: TODO
        :param username: TODO"""
        if self.db.package('adm'):
            username = username or self.currentPage.user if self.currentPage else None
            pkg = pkg or self.currentPage.packageId if self.currentPage else None
            return self.db.table('adm.user').getPreference(path=path, pkg=pkg, dflt=dflt, username=username)
            
    def setUserPreference(self, path, data, pkg=None, username=None):
        """TODO
        
        :param path: TODO
        :param data: TODO
        :param pkg: the :ref:`package <packages>` object
        :param username: TODO"""
        if self.db.package('adm'):
            pkg = pkg or self.currentPage.packageId
            username = username or self.currentPage.user if self.currentPage else None
            self.db.table('adm.user').setPreference(path, data, pkg=pkg, username=username) 

    @property
    def ukeInstanceId(self):
        if not getattr(self,'_ukeInstanceId',None):
            r = self.db.table('uke.instance').getInstanceRecord()
            self._ukeInstanceId = r['id']
            ukeInstance = self.db.application.getAuxInstance('uke')
            if ukeInstance:
                if not ukeInstance.db.table('uke.instance').existsRecord(r['id']):
                    ukeInstance.db.table('uke.instance').insert(r)
                    ukeInstance.db.commit()
        return self._ukeInstanceId
            
    def dropConnectionFolder(self, connection_id=None):
        """:param connection_id: TODO"""
        pathlist = ['data', '_connections']
        if connection_id:
            pathlist.append(connection_id)
        connectionFolder = os.path.join(self.site_path, *pathlist)
        for root, dirs, files in os.walk(connectionFolder, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        if connection_id:
            os.rmdir(connectionFolder)
            
    def lockRecord(self, page, table, pkey):
        """TODO
        
        :param page: TODO
        :param table: the :ref:`database table <table>` name on which the query will be executed,
                      in the form ``packageName.tableName`` (packageName is the name of the
                      :ref:`package <packages>` to which the table belongs to)
        :param pkey: the record :ref:`primary key <pkey>`"""
        if 'sys' in self.gnrapp.db.packages:
            return self.gnrapp.db.table('sys.locked_record').lockRecord(page, table, pkey)
            
    def unlockRecord(self, page, table, pkey):
        """TODO
        
        :param page: TODO
        :param table: the :ref:`database table <table>` name on which the query will be executed,
                      in the form ``packageName.tableName`` (packageName is the name of the
                      :ref:`package <packages>` to which the table belongs to)
        :param pkey: the record :ref:`primary key <pkey>`"""
        if 'sys' in self.gnrapp.db.packages:
            return self.gnrapp.db.table('sys.locked_record').unlockRecord(page, table, pkey)
            
    def clearRecordLocks(self, **kwargs):
        pass

            
    def onClosePage(self, page):
        """A method called on when a page is closed on the client
        
        :param page: the :ref:`webpage` being closed"""
        page_id = page.page_id
        
        self.pageLog('close', page_id=page_id)
        self.clearRecordLocks(page_id=page_id)
        page._closed = True

    def sqlDebugger(self,**kwargs):
        page = self.currentPage
        if page and self.debug:
            page.dev.sqlDebugger.output(page, **kwargs)
            page.sql_count = page.sql_count + 1
            page.sql_time = page.sql_time + kwargs.get('delta_time',0)

    def _get_currentPage(self):
        """property currentPage it returns the page currently used in this thread"""
        return self._currentPages.get(thread.get_ident())
        
    def _set_currentPage(self, page):
        """set currentPage for this thread"""
        self._currentPages[thread.get_ident()] = page
        
    currentPage = property(_get_currentPage, _set_currentPage)


    def _get_currentMaintenance(self):
        """property currentPage it returns the page currently used in this thread"""
        return self._currentMaintenances.get(thread.get_ident())
        
    def _set_currentMaintenance(self, page):
        """set currentPage for this thread"""
        self._currentMaintenances[thread.get_ident()] = page
        
    currentMaintenance = property(_get_currentMaintenance, _set_currentMaintenance)

    def _get_currentRequest(self):
        """property currentRequest it returns the request currently used in this thread"""
        return self._currentRequests.get(thread.get_ident())
        
    def _set_currentRequest(self, request):
        """set currentRequest for this thread"""
        self._currentRequests[thread.get_ident()] = request
        
    currentRequest = property(_get_currentRequest, _set_currentRequest)

    @property
    def heartbeat_options(self):
        heartbeat = boolean(self.config['wsgi?heartbeat'])
        if heartbeat:
            site_url = self.config['wsgi?external_host'] or (self.currentRequest and self.currentRequest.host_url)
            if site_url:
                return dict(interval=60,site_url=site_url)

        
    def callTableScript(self, page=None, table=None, respath=None, class_name=None, runKwargs=None, **kwargs):
        """Call a script from a table's resources (e.g: ``_resources/tables/<table>/<respath>``).
        
        This is typically used to customize prints and batch jobs for a particular installation
        
        :param page: TODO
        :param table: the :ref:`database table <table>` name on which the query will be executed,
                      in the form ``packageName.tableName`` (packageName is the name of the
                      :ref:`package <packages>` to which the table belongs to)
        :param respath: TODO
        :param class_name: TODO
        :param runKwargs: TODO"""
        script = self.loadTableScript(page=page, table=table, respath=respath, class_name=class_name)
        if runKwargs:
            for k, v in runKwargs.items():
                kwargs[str(k)] = v
        result = script(**kwargs)
        return result
        
    def loadTableScript(self, page=None, table=None, respath=None, class_name=None):
        """TODO
        
        :param page: TODO
        :param table: the :ref:`database table <table>` name on which the query will be executed,
                      in the form ``packageName.tableName`` (packageName is the name of the
                      :ref:`package <packages>` to which the table belongs to)
        :param respath: TODO
        :param class_name: TODO"""
        return self.resource_loader.loadTableScript(page=page, table=table, respath=respath, class_name=class_name)
        
    def _get_resources(self):
        if not hasattr(self, '_resources'):
            self._resources = self.resource_loader.site_resources()
        return self._resources
        
    resources = property(_get_resources)
        
    def _get_resources_dirs(self):
        if not hasattr(self, '_resources_dirs'):
            self._resources_dirs = self.resources.values()
            self._resources_dirs.reverse()
        return self._resources_dirs
        
    resources_dirs = property(_get_resources_dirs)
        
    def pkg_page_url(self, pkg, *args):
        """TODO
        
        :param pkg: the :ref:`package <packages>` object"""
        return ('%s%s/%s' % (self.home_uri, pkg, '/'.join(args))).replace('//', '/')
        
    def webtools_url(self, tool, **kwargs):
        """TODO
        
        :param tool: TODO"""
        kwargs_string = '&'.join(['%s=%s' % (k, v) for k, v in kwargs.items()])
        return '%s%s_tools/%s?%s' % (self.external_host, self.home_uri, tool, kwargs_string)
        
    def serve_ping(self, response, environ, start_response, page_id=None, reason=None, **kwargs):
        response.content_type = "text/xml"
        result = self.register.handle_ping(page_id=page_id,reason=reason,**kwargs)
        if result is False:
            return self.failed_exception('no longer existing page %s' % page_id, environ, start_response)
        else:
            return result.toXml(unresolved=True, omitUnknownTypes=True)
                                  
    def parse_kwargs(self, kwargs):
        """TODO
        :param kwargs: the kw arguments
        """
        catalog = self.gnrapp.catalog
        result = dict()
        for k, v in kwargs.items():
            k = k.strip()
            if isinstance(v, basestring):
                try:
                    v = catalog.fromTypedText(v)
                    if isinstance(v, basestring):
                        v = v.decode('utf-8')
                    result[k] = v
                except Exception, e:
                    raise
            else:
                result[k] = v
        return result
        
    @deprecated
    def site_static_path(self, *args):
        """.. warning:: deprecated since version 0.7"""
        return self.getStatic('site').path(*args)
        
    @deprecated
    def site_static_url(self, *args):
        """.. warning:: deprecated since version 0.7"""
        return self.getStatic('site').url(*args)
        

    def shellCall(self,*args):
        return subprocess.Popen(args, stdout=subprocess.PIPE).communicate()[0]

    def extractTextContent(self, filepath=None):
        filename,ext = os.path.splitext(filepath)
        tifname = '%s.tif' %filename
        txtname = '%s.txt' %filename
        try:
            self.shellCall('convert','-density','300',filepath,'-depth','8',tifname)
            self.shellCall('tesseract', tifname, filename)
        except Exception:
            print 'missing tesseract in this installation'
            return
        result = ''
        if not os.path.isfile(txtname):
            return
        with open(txtname,'r') as f:
            result = f.read()
        if os.path.exists(tifname):
            os.remove(tifname)
        if os.path.exists(txtname):
            os.remove(txtname)
        return result

    def zipFiles(self, file_list=None, zipPath=None):
        """Allow to zip one or more files
        
        :param file_list: a string with the files names to be zipped
        :param zipPath: the result path of the zipped file"""
        import zipfile
        
        zipresult = open(zipPath, 'wb')
        zip_archive = zipfile.ZipFile(zipresult, mode='w', compression=zipfile.ZIP_DEFLATED,allowZip64=True)
        for fname in file_list:
            zip_archive.write(fname, os.path.basename(fname))
        zip_archive.close()
        zipresult.close()

    def externalUrl(self, path,serveAsLocalhost=None, _link=False,**kwargs):
        """TODO
        
        :param path: TODO"""
        params = urllib.urlencode(kwargs)
        #path = os.path.join(self.homeUrl(), path)
        if path == '': 
            path = self.home_uri
        cr = self.currentRequest
        path = cr.relative_url(path)
        if serveAsLocalhost:
            path = path.replace(cr.host.replace(':%s'%cr.host_port,''),'localhost')
        if params:
            path = '%s?%s' % (path, params)

        if _link:
            return '<a href="%s" target="_blank">%s</a>' %(path,_link if _link is not True else '')
        return path


        
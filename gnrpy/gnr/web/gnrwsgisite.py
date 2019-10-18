from __future__ import print_function
from future import standard_library
standard_library.install_aliases()
from builtins import str
from past.builtins import basestring
#from builtins import object
from gnr.core.gnrbag import Bag
from werkzeug.wrappers import Request, Response
from webob.exc import WSGIHTTPException, HTTPInternalServerError, HTTPNotFound, HTTPForbidden, HTTPPreconditionFailed, HTTPClientError, HTTPMovedPermanently,HTTPTemporaryRedirect
from gnr.web.gnrwebapp import GnrWsgiWebApp
from gnr.web.gnrwebpage import GnrUnsupportedBrowserException, GnrMaintenanceException
import os
import re
import logging
import subprocess
import urllib.request, urllib.parse, urllib.error
import httplib2
from gnr.core import gnrstring
import six
from time import time
from collections import defaultdict
from gnr.core.gnrlang import deprecated,GnrException,GnrDebugException,tracebackBag
from gnr.core.gnrdecorator import public_method, callers
from gnr.app.gnrconfig import getGnrConfig
from threading import RLock
import _thread
import mimetypes
from gnr.core.gnrsys import expandpath
import pickle
from gnr.core.gnrstring import boolean
from gnr.core.gnrdecorator import extract_kwargs

from gnr.core.gnrprinthandler import PrintHandler
from gnr.web.gnrwebreqresp import GnrWebRequest
from gnr.lib.services import ServiceHandler
from gnr.lib.services.storage import StorageNode
from gnr.app.gnrdeploy import PathResolver

from gnr.web.gnrwsgisite_proxy.gnrresourceloader import ResourceLoader
from gnr.web.gnrwsgisite_proxy.gnrstatichandler import StaticHandlerManager

from gnr.web.gnrwsgisite_proxy.gnrsiteregister import SiteRegisterClient
from gnr.web.gnrwsgisite_proxy.gnrwebsockethandler import WsgiWebSocketHandler
import pdb
from werkzeug import EnvironBuilder
from gnr.web.gnrheadlesspage import GnrHeadlessPage

import warnings

mimetypes.init()

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
        mobilepath = None
        if self.request_kwargs.pop('_mobile',False):
            basepath= self.basepath.replace('webpages','webpages_mobile')
            if os.path.exists(basepath):
                mobilepath = basepath
        pathfile_cache = self.site.pathfile_cache
        for basepath in (mobilepath, self.basepath):
            if not basepath:
                continue
            path_list_copy = list(path_list)
            currpath = []
            while path_list_copy:
                currpath.append(path_list_copy.pop(0))
                searchpath = os.path.splitext(os.path.join(basepath,*currpath))[0]
                cached_path = pathfile_cache.get(searchpath)
                if cached_path is None:
                    cached_path = '%s.py' %searchpath
                    if not os.path.isfile(cached_path):
                        cached_path = False
                    pathfile_cache[searchpath] = cached_path
                if cached_path:
                    self.relpath = cached_path
                    self.request_args = path_list_copy
                    self.basepath = basepath
                    return
            last_path = os.path.join(basepath,*path_list)
            last_index_path = os.path.join(last_path,'index.py')
            if os.path.isfile(last_index_path):
                pathfile_cache[last_path] = last_index_path
                pathfile_cache[last_index_path.replace('.py','')] = last_index_path
                self.relpath = last_index_path
                self.request_args = []
                self.basepath = basepath
                return
        self.basepath = mobilepath or self.basepath
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
                print('***** %s : %s' % (code, msg))
            elif not code:
                print('***** OTHER : %s' % (msg))

    def setDebugAttribute(self, options):
        self.force_debug = False
        if options:
            self.debug = boolean(options.debug)
            if self.debug:
                self.force_debug = True
        else:
            if boolean(self.config['wsgi?debug']) is not True and (self.config['wsgi?debug'] or '').lower()=='force':
                self.debug = True
                self.force_debug = True
            else:
                self.debug = boolean(self.config['wsgi?debug'])


    def __call__(self, environ, start_response):
        return self.wsgiapp(environ, start_response)

    def __init__(self, script_path, site_name=None, _config=None, _gnrconfig=None, counter=None, noclean=None,
                 options=None, tornado=None):
        global GNRSITE
        GNRSITE = self
        counter = int(counter or '0')
        self.pathfile_cache = {}
        self._currentAuxInstanceNames = {}
        self._currentPages = {}
        self._currentRequests = {}
        self._currentMaintenances = {}
        abs_script_path = os.path.abspath(script_path)
        self.remote_db = ''
        self._register = None
        if os.path.isfile(abs_script_path):
            self.site_name = os.path.basename(os.path.dirname(abs_script_path))
        else:
            site_name = site_name or script_path
            if site_name and ':' in site_name:
                site_name,self.remote_db = site_name.split(':',1)
            self.site_name = site_name
        self.site_path = PathResolver().site_name_to_path(self.site_name)
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
        self.default_page = self.config['wsgi?default_page']
        self.root_static = self.config['wsgi?root_static']
        self.websockets= boolean(self.config['wsgi?websockets'])
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
        self.statics = StaticHandlerManager(self)
        self.statics.addAllStatics()
        self.compressedJsPath = None
        self.pages_dir = os.path.join(self.site_path, 'webpages')
        self.site_static_dir = self.config['resources?site'] or '.'
        if self.site_static_dir and not os.path.isabs(self.site_static_dir):
            self.site_static_dir = os.path.normpath(os.path.join(self.site_path, self.site_static_dir))
        self.find_gnrjs_and_dojo()
        self._remote_edit = options.remote_edit if options else None
        self._main_gnrapp = self.build_gnrapp(options=options)
        self.server_locale = self.gnrapp.locale
        self.wsgiapp = self.build_wsgiapp(options=options)
        self.dbstores = self.db.dbstores
        self.resource_loader = ResourceLoader(self)
        self.page_factory_lock = RLock()
        self.webtools = self.resource_loader.find_webtools()
        self.register
        if counter == 0 and self.debug:
            self.onInited(clean=not noclean)
        if counter == 0 and options and options.source_instance:
            self.gnrapp.importFromSourceInstance(options.source_instance)
            self.db.commit()
            print('End of import')

        cleanup = self.custom_config.getAttr('cleanup') or dict()
        self.cleanup_interval = int(cleanup.get('interval') or 120)
        self.page_max_age = int(cleanup.get('page_max_age') or 120)
        self.connection_max_age = int(cleanup.get('connection_max_age')or 600)
        self.db.closeConnection()

    @property
    def db(self):
        return self.gnrapp.db
    
    @property
    def gnrapp(self):
        if self.currentAuxInstanceName:
            return self._main_gnrapp.getAuxInstance(self.currentAuxInstanceName)
        return self._main_gnrapp

    @property
    def services_handler(self):
        if not hasattr(self,'_services_handler'):
            self._services_handler = ServiceHandler(self)
        return self._services_handler
    
    @property
    def mainpackage(self):
        return self.config['wsgi?mainpackage'] or self.gnrapp.packages.keys()[-1]


    def siteConfigPath(self):
        siteConfigPath = os.path.join(self.site_path,'siteconfig.xml')
        if os.path.exists(siteConfigPath):
            return siteConfigPath
        siteConfigPath = os.path.join(self.getInstanceFolder(),'config','siteconfig.xml')
        if os.path.exists(siteConfigPath):
            return siteConfigPath

    def getInstanceFolder(self):
        return PathResolver().instance_name_to_path(self.site_name)

    @property
    def wsk(self):
        if not self.websockets:
            return
        if not hasattr(self,'_wsk'):
            wsk = WsgiWebSocketHandler(self)
            if self.websockets=='required' or wsk.checkSocket():
                self._wsk = wsk
            else:
                self.websockets = False
                return
        return self._wsk

    @property
    def register(self):
        if self._register is None:
            self._register = SiteRegisterClient(self)
            self.checkPendingConnection()
        return self._register

    def getSubscribedTables(self,tables):
        if self._register is not None:
            return self.register.filter_subscribed_tables(tables,register_name='page')

    @property
    def connectionLogEnabled(self):
        if not hasattr(self,'_connectionLogEnabled'):
            if not self.db.package('adm'):
                self._connectionLogEnabled = False
            else:
                self._connectionLogEnabled = self.getPreference('dev.connection_log_enabled',pkg='adm')
        return self._connectionLogEnabled


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
                    for k,v in list(attr.items()):
                        self.extraFeatures['%s_%s' %(n.label,k)] = v



    def getService(self, service_type=None,service_name=None, **kwargs):
        return self.services_handler.getService(service_type=service_type,service_name=service_name or service_type, **kwargs)

    def addStatic(self, static_handler_factory, **kwargs):
        """TODO

        :param service_handler_factory: TODO"""
        return self.statics.add(static_handler_factory, **kwargs)

    def getVolumeService(self, storage_name=None):
        sitevolumes = self.config.getItem('volumes')
        if sitevolumes and storage_name in sitevolumes:
            vpath = sitevolumes.getAttr(storage_name,'path')
        else:
            vpath = storage_name
        volume_path = expandpath(os.path.join(self.site_static_dir,vpath))
        return self.getService(service_type='storage',service_name=storage_name
            ,implementation='local',base_path=volume_path)

    def storagePath(self, storage_name, storage_path):
        if storage_name == 'user':
            return '%s/%s'%(self.currentPage.user, storage_path)
        elif storage_name == 'conn':
            return '%s/%s'%(self.currentPage.connection_id, storage_path)
        elif storage_name == 'page':
            return '%s/%s/%s'% (self.currentPage.connection_id, self.currentPage.page_id, storage_path)
        return storage_path

    def storage(self, storage_name,**kwargs):
        storage = self.getService(service_type='storage',service_name=storage_name)
        if not storage: 
            storage = self.getVolumeService(storage_name=storage_name)
        return storage

    def storageNode(self,*args,**kwargs):
        if isinstance(args[0], StorageNode):
            if args[1:]:
                return self.storageNode(args[0].fullpath, args[1:])
            else:
                return args[0]
        path = '/'.join(args)
        if not ':' in path:
            path = '_raw_:%s'%path
        service_name, storage_path = path.split(':',1)
        storage_path = storage_path.lstrip('/')
        if service_name == 'vol':
            #for legacy path
            service_name, storage_path = storage_path.replace(':','/').split('/', 1) 
        service = self.storage(service_name)
        if kwargs.pop('_adapt', True):
            storage_path = self.storagePath(service_name, storage_path)
        if not service: return
        autocreate = kwargs.pop('autocreate', False)
        must_exist = kwargs.pop('must_exist', False)
        mode = kwargs.pop('mode', None)

        return StorageNode(parent=self, path=storage_path, service=service,
            autocreate=autocreate, must_exist=must_exist, mode=mode)

    def build_lazydoc(self,lazydoc,fullpath=None,temp_dbstore=None,**kwargs):
        ext = os.path.splitext(fullpath)[1]
        ext = ext.replace('.','') if ext else None 
        if lazydoc.startswith('service:'):
            return  self.getService(lazydoc.split(':')[1])(fullpath=fullpath) is not False
        table,pkey,method = gnrstring.splitAndStrip(lazydoc,sep=',',fixed=3)
        dflt_method = 'create_cached_document_%s' %ext if ext else 'create_cached_document'
        m = getattr(self.db.table(table),(method or dflt_method),None)
        if m:
            self.currentPage = self.dummyPage
            if temp_dbstore:
                self.currentPage.dbstore = temp_dbstore
                self.currentPage.db.currentEnv['storename'] = temp_dbstore
            result = m(pkey)
            return result is not False

    def storageDispatcher(self,path_list,environ, start_response,**kwargs):
        if ':' in path_list[0]:
            storage_name, first = path_list.pop(0).split(':')
            path_list.insert(0, first)
        else:
            prefix = path_list.pop(0)[1:] # leva _
            if prefix != 'storage':
                storage_name = prefix
            else:
                storage_name = path_list.pop(0)
        path = '/'.join(path_list)
        storageNode = self.storageNode('%s:%s'%(storage_name,path),_adapt=False)
        exists = storageNode and storageNode.exists
        if not exists and '_lazydoc' in kwargs:
            #fullpath = None ### QUI NON DOBBIAMO USARE I FULLPATH
            exists = self.build_lazydoc(kwargs['_lazydoc'],fullpath=storageNode.internal_path,**kwargs) 
            exists = exists and storageNode.exists
        self.db.closeConnection()
        if not exists:
            if kwargs.get('_lazydoc'):
                headers = []
                start_response('200 OK', headers)
                return ['']
            return self.not_found_exception(environ, start_response)
        return storageNode.serve(environ, start_response,**kwargs)

    #@callers()
    def getStaticPath(self, static, *args, **kwargs):
        """TODO

        :param static: TODO"""
        static_name, static_path = static.split(':',1)
        
        symbolic = kwargs.pop('symbolic', False)
        if symbolic:
            return self.storageNode(static, *args).fullpath
        autocreate = kwargs.pop('autocreate', False)
        if not ':' in static:
            return static

        args = self.adaptStaticArgs(static_name, static_path, args)
        static_handler = self.getStatic(static_name)
        if autocreate and static_handler.supports_autocreate:
            assert autocreate == True or autocreate < 0
            if autocreate != True:
                autocreate_args = args[:autocreate]
            else:
                autocreate_args = args
            dest_dir = static_handler.path(*autocreate_args)
            if not os.path.exists(dest_dir):
                os.makedirs(dest_dir)
        dest_path = static_handler.path(*args)
        return dest_path


    def getStaticUrl(self, static, *args, **kwargs):
        """TODO

        :param static: TODO"""
        if not ':' in static:
            return static
        static_name, static_url = static.split(':',1)
        args = self.adaptStaticArgs(static_name, static_url, args)
        return self.storage(static_name).url(*args, **kwargs)

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
        if self.currentPage and hasattr(self.currentPage, 'localizerKw'):
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
        self.register.on_reloader_restart()
        #self.shared_data.dump()

    def on_site_stop(self):
        """TODO"""
        self.register.on_site_stop()


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

    def load_site_config(self,external_site=None):
        """TODO"""
        return PathResolver().get_siteconfig(external_site or self.site_name)

    def external_site_config(self,sitename):
        return self.load_site_config(external_site=sitename)

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
                    for k,v in list(attr.items()):
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
        return self.server_locale

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
        url= urllib.request.urlopen(url,urllib.parse.urlencode(kwargs))
        return url.read()

    def callGnrRpcUrl(self,url,method,*args,**kwargs):
        kwargs = kwargs or dict()
        for k in kwargs:
            kwargs[k] = self.gnrapp.catalog.asTypedText(kwargs[k])
        urlargs = [url,method]+list(args)
        url = '/'.join(urlargs)
        http = httplib2.Http()
        headers = {'Content-type': 'application/x-www-form-urlencoded'}
        response,content = http.request(url, 'POST', headers=headers, body=urllib.parse.urlencode(kwargs))
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
        except Exception as writingErrorException:
            print('\n ####writingErrorException %s for exception %s' %(str(writingErrorException),str(exception)))

    @public_method
    def writeError(self, description=None,error_type=None, **kwargs):
        try:
            page = self.currentPage
            user, user_ip, user_agent = (page.user, page.user_ip, page.user_agent) if page else (None, None, None)
            self.db.table('sys.error').writeError(description=description,error_type=error_type,user=user,user_ip=user_ip,user_agent=user_agent,**kwargs)
        except Exception as e:
            print(str(e))
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
        #if path_info.endswith('.py'):
        #    path_info = path_info[:-3]
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

    def parse_request_params(self, request):
        """TODO

        :param params: TODO"""
        out_dict = dict()
        for source in (request.values, request.files):
            for name,value in source.lists():
                try:
                    name = str(name)
                    if len(value)==1:
                        out_dict[name]=value[0]
                    else:
                        out_dict[name] = value
                except UnicodeDecodeError:
                    pass
        return out_dict

    @property
    def dummyPage(self):
        environ_builder = EnvironBuilder(method='GET',path='/sys/headless')
        request = Request(environ_builder.get_environ())
        response = Response()
        page = self.resource_loader(['sys', 'headless'], request, response)
        page.locale = self.server_locale
        return page

    def virtualPage(self, table=None,table_resources=None,py_requires=None):
        page = self.dummyPage
        if table and table_resources:
            for path in table_resources.split(','):
                page.mixinTableResource(table=table,path=path)

        if py_requires:
            for path in py_requires.split(','):
                page.mixinComponent(path)
        return page

    @property
    def isInMaintenance(self):
        request = self.currentRequest
        request_kwargs = self.parse_kwargs(self.parse_request_params(request))
        path_list = self.get_path_list(request.path)
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
            user = c.get('user') if c else None
            return self.register.isInMaintenance(user)

    def dispatcher(self, environ, start_response):
        self.currentRequest = Request(environ)
        if self.isInMaintenance:
            return self.maintenanceDispatcher(environ, start_response)
        else:
            try:
                return self._dispatcher(environ, start_response)
            except self.register.errors.ConnectionClosedError:
                self.currentMaintenance = 'register_error'
                self._register = None
                return self.maintenanceDispatcher(environ, start_response)
            except Exception as e:
                page = self.currentPage
                if self.debug and ((page and page.isDeveloper()) or self.force_debug):
                    raise
                self.writeException(exception=e,traceback=tracebackBag())
                exc = HTTPInternalServerError(
                    'Internal server error',
                    comment='SCRIPT_NAME=%r; PATH_INFO=%r;'
                    % (environ.get('SCRIPT_NAME'), environ.get('PATH_INFO')))
                return exc(environ, start_response)

    def maintenanceDispatcher(self,environ, start_response):
        request = self.currentRequest
        response = Response()
        response.mimetype = 'text/html'
        request_kwargs = self.parse_kwargs(self.parse_request_params(request))
        path_list = self.get_path_list(request.path)
        if (path_list and path_list[0].startswith('_')) or ('method' in request_kwargs or 'rpc' in request_kwargs or '_plugin' in request_kwargs):
            response = self.setResultInResponse('maintenance', response, info_GnrSiteMaintenance=self.currentMaintenance)
            return response(environ, start_response)
        else:
            return self.serve_htmlPage('html_pages/maintenance.html', environ, start_response)

    @property
    def external_host(self):
        return self.currentPage.external_host if (self.currentPage and hasattr(self.currentPage,'request')) else self.configurationItem('wsgi?external_host',mandatory=True)

    def configurationItem(self,path,mandatory=False):
        result = self.config[path]
        if mandatory and result is None:
            print('Missing mandatory configuration item: %s' %path)
        return result

    def _dispatcher(self, environ, start_response):
        """Main :ref:`wsgi` dispatcher, calls serve_staticfile for static files and
        self.createWebpage for :ref:`gnrcustomwebpage`

        :param environ: TODO
        :param start_response: TODO"""
        self.currentPage = None
        t = time()
        request = self.currentRequest
        response = Response()
        response.mimetype = 'text/html'
        # Url parsing start
        path_list = self.get_path_list(request.path)
        expiredConnections = self.register.cleanup()
        if expiredConnections:
            self.connectionLog('close',expiredConnections)
        if path_list == ['favicon.ico']:
            path_list = ['_site', 'favicon.ico']
            self.log_print('', code='FAVICON')
            # return response(environ, start_response)
        request_kwargs = self.parse_kwargs(self.parse_request_params(request))
        self.currentAuxInstanceName = request_kwargs.get('aux_instance')
        user_agent = request.user_agent.string or ''
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
            except Exception as exc:
                raise
            finally:
                self.cleanup()
            return response(environ, start_response)

        #static elements that doesn't have .py extension in self.root_static
        if  self.root_static and path_list and not path_list[0].startswith('_') and '.' in path_list[-1] and not (':' in path_list[0]):
            if path_list[-1].split('.')[-1]!='py':
                path_list = self.root_static.split('/')+path_list
        
        if path_list and path_list[0].startswith('_tools'):
            self.log_print('%s : kwargs: %s' % (path_list, str(request_kwargs)), code='TOOLS')
            return self.serve_tool(path_list, environ, start_response, **request_kwargs)
        elif path_list and (':' in path_list[0] or path_list[0].startswith('_storage') or \
            path_list[0].startswith('_site') or path_list[0].startswith('_rsrc') or \
            path_list[0].startswith('_dojo') or path_list[0].startswith('_pkg') or \
            path_list[0].startswith('_gnr') or path_list[0].startswith('_pages') or \
            path_list[0].startswith('_conn') or path_list[0].startswith('_user') or \
            path_list[0].startswith('_pages') or path_list[0].startswith('_vol')):
            self.log_print('%s : kwargs: %s' % (path_list, str(request_kwargs)), code='STORAGE')
            return self.storageDispatcher(path_list, environ, start_response, **request_kwargs)
        elif path_list and path_list[0].startswith('_'):
            self.log_print('%s : kwargs: %s' % (path_list, str(request_kwargs)), code='STATIC')
            try:
                return self.statics.static_dispatcher(path_list, environ, start_response, **request_kwargs)
            except GnrDebugException as exc:
                raise
            except Exception as exc:
                return self.not_found_exception(environ,start_response)
        else:
            self.log_print('%s : kwargs: %s' % (path_list, str(request_kwargs)), code='RESOURCE')
            try:
                page = self.resource_loader(path_list, request, response, environ=environ,request_kwargs=request_kwargs)
                if page:
                    page.download_name = download_name
            except WSGIHTTPException as exc:
                return exc(environ, start_response)
            except Exception as exc:
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
                    download_name = str(page.download_name)
                    content_type = getattr(page,'forced_mimetype',None) or mimetypes.guess_type(download_name)[0]
                    if content_type:
                        page.response.content_type = content_type
                    page.response.add_header("Content-Disposition", str("attachment; filename=%s" %download_name))
                import io
                try:
                    file_types = file, io.IOBase
                except NameError:
                    file_types = (io.IOBase,)
                if isinstance(result, file_types):
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
                                                                forced_headers=page.getForcedHeaders(),
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
        dbstore = None
        if first.startswith('@'):
            instanceNode = self.gnrapp.config.getNode('aux_instances.%s' %first[1:])
        else:
            dbstore = self.db.stores_handler.get_dbstore(first)
        if dbstore or instanceNode:
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
    def setResultInResponse(self, result, response,info_kwargs=None,forced_headers=None,**kwargs):
        """TODO

        :param result: TODO
        :param response: TODO
        :param totaltime: TODO"""
        if forced_headers:
            for k,v in list(forced_headers.items()):
                response.headers[k] = str(v)
        for k,v in list(info_kwargs.items()):
            if v is not None:
                if six.PY2:
                    v=unicode(v)
                else:
                    v=str(v)
                response.headers['X-%s' %k] = v
        #if six.PY2 and isinstance(result, unicode):
        #    response.data=result
        if isinstance(result, str):
            #response.mimetype = kwargs.get('mimetype') or 'text/plain'
            #print(f'response mimetipe {response.mimetype} content_type {response.content_type}')
            response.mimetype = kwargs.get('mimetype') or response.mimetype or 'text/plain'
            response.data=result # PendingDeprecationWarning: .unicode_body is deprecated in favour of Response.text
        
        elif isinstance(result, basestring):
            response.data=result
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

        if isinstance(result, str):
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

    def redirect(self, environ, start_response, location=None,temporary=False):
        if temporary:
            exc = HTTPTemporaryRedirect(location=location)
        else:
            exc = HTTPMovedPermanently(location=location)
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
            pass
            #wsgiapp = SafeEvalException(wsgiapp, debug=True)
        else:
            err_kwargs = dict(debug=True)
            if 'debug_email' in self.config:
                error_smtp_kwargs = self.config.getAttr('debug_email')
                if error_smtp_kwargs.get('smtp_password'):
                    error_smtp_kwargs['smtp_password'] = error_smtp_kwargs['smtp_password'].encode('utf-8')
                if error_smtp_kwargs.get('smtp_username'):
                    error_smtp_kwargs['smtp_username'] = error_smtp_kwargs['smtp_username'].encode('utf-8')
                if 'error_subject_prefix' not in error_smtp_kwargs:
                    error_smtp_kwargs['error_subject_prefix'] = '[%s] ' % self.site_name
                error_smtp_kwargs['error_email'] = error_smtp_kwargs['error_email'].replace(';', ',').split(',')
                if 'smtp_use_tls' in error_smtp_kwargs:
                    error_smtp_kwargs['smtp_use_tls'] = (error_smtp_kwargs['smtp_use_tls'] in (True, 'true', 't', 'True', '1', 'TRUE'))
                self.error_smtp_kwargs = dict(error_smtp_kwargs)
                self.error_smtp_kwargs['error_email_from'] = self.error_smtp_kwargs.pop('from_address')
                err_kwargs.update(error_smtp_kwargs)
                #wsgiapp = ErrorMiddleware(wsgiapp, **err_kwargs)
        return wsgiapp

    def build_gnrapp(self, options=None):
        """Builds the GnrApp associated with this site"""
        instance_path = os.path.join(self.site_path, 'instance')
        if not os.path.isdir(instance_path):
            instance_path = self.getInstanceFolder()
        if not os.path.isdir(instance_path):
            instance_path = self.config['instance?path'] or self.config['instances.#0?path']
        self.instance_path = instance_path
        #restorepath = self.option_restore
        restorepath = options.restore if options else None
        restorefiles=[]
 #      if restorepath:
 #           if restorepath == 'auto':
 #               restorepath = self.getStaticPath('site:maintenance','restore',autocreate=True)
 #               restorefiles = [j for j in os.listdir(restorepath) if not j.startswith('.')]
 #           else:
 #               restorefiles = [restorepath]
 #           if restorefiles:
 #               restorepath = os.path.join(restorepath,restorefiles[0])
 #           else:
 #               restorepath = None
        if self.remote_db:
            instance_path = '%s@%s' %(instance_path,self.remote_db)
        app = GnrWsgiWebApp(instance_path, site=self,restorepath=restorepath)
        self.config.setItem('instances.app', app, path=instance_path)
 #       for f in restorefiles:
 #           if os.path.isfile(restorepath):
 #               os.rename(restorepath,self.getStaticPath('site:maintenance','restored',f,autocreate=-1))
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

    def getPreference(self, path, pkg=None, dflt=None, mandatoryMsg=None):
        """TODO

        :param path: TODO
        :param pkg: the :ref:`package <packages>` object
        :param dflt: TODO"""
        if self.db.package('adm'):
            pkg = pkg or self.currentPage.packageId
            return self.db.table('adm.preference').getPreference(path, pkg=pkg, dflt=dflt, mandatoryMsg=mandatoryMsg)

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
        if page and self.debug and page.debug_sql:
            page.dev.sqlDebugger.output(page, **kwargs)
            page.sql_count = page.sql_count + 1
            page.sql_time = page.sql_time + kwargs.get('delta_time',0)

    def _get_currentPage(self):
        """property currentPage it returns the page currently used in this thread"""
        return self._currentPages.get(_thread.get_ident())

    def _set_currentPage(self, page):
        """set currentPage for this thread"""
        self._currentPages[_thread.get_ident()] = page

    currentPage = property(_get_currentPage, _set_currentPage)

    def _get_currentAuxInstanceName(self):
        """property currentAuxInstanceName it returns the page currently used in this thread"""
        return self._currentAuxInstanceNames.get(_thread.get_ident())

    def _set_currentAuxInstanceName(self, auxInstance):
        """set currentAuxInstanceName for this thread"""
        self._currentAuxInstanceNames[_thread.get_ident()] = auxInstance

    currentAuxInstanceName = property(_get_currentAuxInstanceName, _set_currentAuxInstanceName)


    def _get_currentMaintenance(self):
        """property currentPage it returns the page currently used in this thread"""
        return self._currentMaintenances.get(_thread.get_ident())

    def _set_currentMaintenance(self, page):
        """set currentPage for this thread"""
        self._currentMaintenances[_thread.get_ident()] = page

    currentMaintenance = property(_get_currentMaintenance, _set_currentMaintenance)

    def _get_currentRequest(self):
        """property currentRequest it returns the request currently used in this thread"""
        return self._currentRequests.get(_thread.get_ident())

    def _set_currentRequest(self, request):
        """set currentRequest for this thread"""
        self._currentRequests[_thread.get_ident()] = request

    currentRequest = property(_get_currentRequest, _set_currentRequest)

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
            for k, v in list(runKwargs.items()):
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
            self._resources_dirs = list(self.resources.values())
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
        kwargs_string = '&'.join(['%s=%s' % (k, v) for k, v in list(kwargs.items())])
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
        for k, v in list(kwargs.items()):
            k = k.strip()
            if isinstance(v, basestring):
                try:
                    v = catalog.fromTypedText(v)
                    if isinstance(v, basestring) and six.PY2:
                        v = v.decode('utf-8')
                    result[k] = v
                except Exception as e:
                    raise
            else:
                result[k] = v
        return result

    @deprecated
    def site_static_path(self, *args):
        """.. warning:: deprecated since version 0.7"""
        return self.storage('site').path(*args)

    @deprecated
    def site_static_url(self, *args):
        """.. warning:: deprecated since version 0.7"""
        return self.storage('site').url(*args)


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
            print('missing tesseract in this installation')
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

    def uploadFile(self,file_handle=None,dataUrl=None,filename=None,uploadPath=None):
        if file_handle is not None:
            f = file_handle.stream
            content = f.read()
            original_filename = os.path.basename(file_handle.filename)
            original_ext = os.path.splitext(original_filename)[1]
            filename = filename or original_filename
        elif dataUrl:
            import base64
            dataUrlPattern = re.compile('data:(.*);base64,(.*)$')
            g= dataUrlPattern.match(dataUrl)#.group(2)
            mimetype,base64Content = g.groups()
            original_ext = mimetypes.guess_extension(mimetype)
            content = base64.b64decode(base64Content)
        else:
            return None,None
        file_ext = os.path.splitext(filename)[1]
        if not file_ext:
            filename = '%s%s' %(filename,original_ext)
            file_ext = original_ext
        file_node = self.storageNode(uploadPath, filename,autocreate=-1)
        file_path = file_node.fullpath
        file_url = file_node.url()
        with file_node.open(mode='wb') as outfile:
            outfile.write(content)
        return file_path,file_url

    def zipFiles(self, file_list=None, zipPath=None):
        """Allow to zip one or more files

        :param file_list: a string with the files names to be zipped
        :param zipPath: the result path of the zipped file"""
        import zipfile
        zipresult = self.storageNode(zipPath)
        if isinstance(file_list,basestring):
            file_list = file_list.split(',')
        with zipresult.open(mode='wb') as zipresult:
            zip_archive = zipfile.ZipFile(zipresult, mode='w', compression=zipfile.ZIP_DEFLATED,allowZip64=True)
            for fpath in file_list:
                newname = None
                if isinstance(fpath,tuple):
                    fpath,newname = fpath
                fpath = self.storageNode(fpath)
                if fpath.isdir:
                    self._zipDirectory(fpath,zip_archive)
                    continue
                if not newname:
                    newname = fpath.basename
                with fpath.local_path(mode='r') as local_path:
                    zip_archive.write(local_path, newname)
            zip_archive.close()

    def _zipDirectory(self,path, zip_archive):
        from gnr.lib.services.storage import StorageResolver
        def cb(n):
            if n.attr.get('file_ext')!='directory':
                fpath = self.storageNode(n.attr['abs_path'])
                with fpath.local_path(mode='r') as local_path:
                    zip_archive.write(local_path,n.attr['rel_path'])
        dirres = StorageResolver(path)
        dirres().walk(cb,_mode='')

        
    def externalUrl(self, path, _link=False,**kwargs):
        """TODO

        :param path: TODO"""
        params = urllib.parse.urlencode(kwargs)
        #path = os.path.join(self.homeUrl(), path)
        if path == '':
            path = self.home_uri
        f =  '{}{}' if path.startswith('/') else '{}/{}'
        path = f.format(self.external_host,path)
        if params:
            path = '%s?%s' % (path, params)
        if _link:
            return '<a href="%s" target="_blank">%s</a>' %(path,_link if _link is not True else '')
        return path

#-*- coding: UTF-8 -*-
#--------------------------------------------------------------------------
# package           : GenroPy web - see LICENSE for details
# module gnrwebcore : core module for genropy web framework
# Copyright (c)     : 2004 - 2007 Softwell sas - Milano 
# Written by    : Giovanni Porcari, Michele Bertoldi
#                 Saverio Porcari, Francesco Porcari , Francesco Cavazzana
#--------------------------------------------------------------------------
#This library is free software; you can redistribute it and/or
#modify it under the terms of the GNU Lesser General Public
#License as published by the Free Software Foundation; either
#version 2.1 of the License, or (at your option) any later version.

#This library is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
#Lesser General Public License for more details.

#You should have received a copy of the GNU Lesser General Public
#License along with this library; if not, write to the Free Software
#Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA

#Created by Giovanni Porcari on 2007-03-24.
#Copyright (c) 2007 Softwell. All rights reserved.

import urllib
from gnr.web._gnrbasewebpage import GnrBaseWebPage
import os
import shutil

from gnr.core.gnrstring import toText, toJson, concat, jsquote,splitAndStrip

from gnr.core.gnrlang import getUuid
from mako.lookup import TemplateLookup
from gnr.web.gnrwebreqresp import GnrWebRequest, GnrWebResponse
from gnr.web.gnrwebpage_proxy.apphandler import GnrWebAppHandler
from gnr.web.gnrwebpage_proxy.connection import GnrWebConnection
from gnr.web.gnrwebpage_proxy.serverbatch import GnrWebBatch
from gnr.web.gnrwebpage_proxy.rpc import GnrWebRpc
from gnr.web.gnrwebpage_proxy.localizer import GnrWebLocalizer
from gnr.web.gnrwebpage_proxy.debugger import GnrWebDebugger
from gnr.web.gnrwebpage_proxy.utils import GnrWebUtils
from gnr.web.gnrwebpage_proxy.pluginhandler import GnrWebPluginHandler
from gnr.web.gnrwebpage_proxy.jstools import GnrWebJSTools
from gnr.web.gnrwebstruct import GnrGridStruct, struct_method
from gnr.core.gnrlang import gnrImport, GnrException
from gnr.core.gnrbag import Bag, BagResolver,BagCbResolver
from gnr.core.gnrlang import deprecated
from gnr.web.gnrbaseclasses import BaseComponent # DO NOT REMOVE, old code relies on BaseComponent being defined in this file

import datetime

AUTH_OK = 0
AUTH_NOT_LOGGED = 1
AUTH_FORBIDDEN = -1
PAGE_TIMEOUT = 60
PAGE_REFRESH = 20

class GnrWebPageException(GnrException):
    pass
    
class GnrWebPage(GnrBaseWebPage):
    """add???"""
    def __init__(self, site=None, request=None, response=None, request_kwargs=None, request_args=None, filepath=None,
                 packageId=None, basename=None, environ=None):
        self.site = site
        self.user_agent = request.user_agent or []
        self.user_ip = request.remote_addr
        self._environ = environ
        self.isTouchDevice = ('iPad' in self.user_agent or 'iPhone' in self.user_agent)
        self._event_subscribers = {}
        self.local_datachanges = list()
        self.forked = False # maybe redefine as _forked
        self.filepath = filepath
        self.packageId = packageId
        self.basename = basename
        self.siteFolder = self.site.site_path
        self.folders = self._get_folders()
        self.called_url = request.url
        self.path_url = request.path_url
        self.request = GnrWebRequest(request)
        self.response = GnrWebResponse(response)
        self._request = self.request._request
        self._response = self.response._response
        self.response.add_header('Pragma', 'no-cache')
        self._htmlHeaders = []
        self._pendingContextToCreate = []
        self.pagename = os.path.splitext(os.path.basename(self.filepath))[0].split(os.path.sep)[-1]
        self.pagepath = self.filepath.replace(self.folders['pages'], '')
        self.debug_mode = False
        self._dbconnection = None
        self._user_login = request_kwargs.pop('_user_login', None)
        self.page_timeout = self.site.config.getItem('page_timeout') or PAGE_TIMEOUT
        self.page_refresh = self.site.config.getItem('page_refresh') or PAGE_REFRESH
        self.private_kwargs = dict([(k[:2], v)for k, v in request_kwargs.items() if k.startswith('__')])
        self.pagetemplate = request_kwargs.pop('pagetemplate', None) or getattr(self, 'pagetemplate', None) or \
                            self.site.config['dojo?pagetemplate'] or 'standard.tpl'
        self.css_theme = request_kwargs.pop('css_theme', None) or getattr(self, 'css_theme', None) or self.site.config[
                                                                                                      'gui?css_theme']
        self.dojo_theme = request_kwargs.pop('dojo_theme', None) or getattr(self, 'dojo_theme', None)
        self.dojo_version = request_kwargs.pop('dojo_version', None) or getattr(self, 'dojo_version', None)
        self.debugopt = request_kwargs.pop('debugopt', None)
            
        self.callcounter = request_kwargs.pop('callcounter', None) or 'begin'
        if not hasattr(self, 'dojo_source'):
            self.dojo_source = self.site.config['dojo?source']
        if 'dojo_source' in request_kwargs:
            self.dojo_source = request_kwargs.pop('dojo_source')
        self.connection = GnrWebConnection(self,
                                           connection_id=request_kwargs.pop('_connection_id', None),
                                           user=request_kwargs.pop('_user', None))
        page_id = request_kwargs.pop('page_id', None)
        self.instantiateProxies()
        self.onPreIniting(request_args, request_kwargs)
        self._call_handler = self.get_call_handler(request_args, request_kwargs)
        self.page_item = self._check_page_id(page_id, kwargs=request_kwargs)
        self._workdate = self.page_item['data']['workdate'] #or datetime.date.today()
        self.onIniting(request_args, request_kwargs)
        self._call_args = request_args or tuple()
        self._call_kwargs = request_kwargs or {}
            
    def onPreIniting(self, *request_args, **request_kwargs):
        """add???"""
        pass

    def instantiateProxies(self):
        proxy_classes = [(p[:-11],getattr(self,p, None)) for p in dir(self) if p.endswith('_proxyclass')]
        for proxy_name,proxy_class in proxy_classes:
            if proxy_class:
                setattr(self,proxy_name,proxy_class(self))

    def _check_page_id(self, page_id=None, kwargs=None):
        if page_id:
            if not self.connection.connection_id:
                raise self.site.client_exception('The connection is not longer valid', self._environ)
            if not self.connection.validate_page_id(page_id):
                raise self.site.client_exception('The referenced page_id is not valid in this connection',
                                                 self._environ)
            page_item = self.site.register.page(page_id)
            if not page_item:
                raise self.site.client_exception('The referenced page_id is cannot be found in site register',
                                                 self._environ)
            self.page_id = page_id
            return page_item
        else:
            if self._call_handler_type in ('pageCall', 'externalCall'):
                raise self.site.client_exception('The request must reference a page_id', self._environ)
            if not self.connection.connection_id:
                self.connection.create()
            self.page_id = getUuid()
            workdate = kwargs.pop('_workdate_', None)# or datetime.date.today()
            return self.site.register.new_page(self.page_id, self, data=dict(pageArgs=kwargs, workdate=workdate))
            
    def get_call_handler(self, request_args, request_kwargs):
        """add???
        
        :param request_args: add???
        :param request_kwargs: add???
        :returns: add???
        """
        if '_plugin' in request_kwargs:
            self._call_handler_type = 'plugin'
            return self.pluginhandler.get_plugin(request_kwargs['_plugin'], request_args=request_args,
                                                 request_kwargs=request_kwargs)
        elif 'rpc' in request_kwargs:
            self._call_handler_type = 'externalCall'
            return self.getPublicMethod('rpc', request_kwargs.pop('rpc'))
        elif 'method' in request_kwargs:
            self._call_handler_type = 'pageCall'
            return self._rpcDispatcher
        else:
            self._call_handler_type = 'root'
            return self.rootPage
            
        # ##### BEGIN: PROXY DEFINITION ########
        
    def _get_frontend(self):
        if not hasattr(self, '_frontend'):
            if not hasattr(self, 'page_frontend') and hasattr(self, 'dojo_version'):
                self.page_frontend = 'dojo_%s' % self.dojo_version
            frontend_module = gnrImport('gnr.web.gnrwebpage_proxy.frontend.%s' % self.page_frontend)
            frontend_class = getattr(frontend_module, 'GnrWebFrontend')
            self._frontend = frontend_class(self)
        return self._frontend
        
    frontend = property(_get_frontend)
        
    def _get_localizer(self):
        if not hasattr(self, '_localizer'):
            self._localizer = GnrWebLocalizer(self)
        return self._localizer
        
    localizer = property(_get_localizer)
        
    def _get_debugger(self):
        if not hasattr(self, '_debugger'):
            self._debugger = GnrWebDebugger(self)
        return self._debugger
        
    debugger = property(_get_debugger)
        
    def _get_utils(self):
        if not hasattr(self, '_utils'):
            self._utils = GnrWebUtils(self)
        return self._utils
        
    utils = property(_get_utils)
        
    def _get_rpc(self):
        if not hasattr(self, '_rpc'):
            self._rpc = GnrWebRpc(self)
        return self._rpc
        
    rpc = property(_get_rpc)
        
    def _get_pluginhandler(self):
        if not hasattr(self, '_pluginhandler'):
            self._pluginhandler = GnrWebPluginHandler(self)
        return self._pluginhandler
        
    pluginhandler = property(_get_pluginhandler)
        
    def _get_jstools(self):
        if not hasattr(self, '_jstools'):
            self._jstools = GnrWebJSTools(self)
        return self._jstools
        
    jstools = property(_get_jstools)
        
    def _get_db(self):
        if not hasattr(self, '_db'):
            self._db = self.application.db
            self._db.updateEnv(storename=getattr(self, 'storename', None), workdate=self.workdate, locale=self.locale,
                               user=self.user, userTags=self.userTags, pagename=self.pagename)
            avatar = self.avatar
            if avatar:
                self._db.updateEnv(**self.avatar.extra_kwargs)
            storeDbEnv = self.pageStore().getItem('dbenv')
            if storeDbEnv:
                self._db.updateEnv(**dict(storeDbEnv))
                    
            for dbenv in [getattr(self, x) for x in dir(self) if x.startswith('dbenv_')]:
                kwargs = dbenv() or {}
                self._db.updateEnv(**kwargs)
        return self._db
        
    db = property(_get_db)
        
    def _get_workdate(self):
        return self._workdate or datetime.date.today()
        
    def _set_workdate(self, workdate):
        with self.pageStore() as store:
            store.setItem('workdate', workdate)
        self._workdate = workdate
        self.db.workdate = workdate
        
    workdate = property(_get_workdate, _set_workdate)
    ###### END: PROXY DEFINITION #########
        
    def __call__(self):
        """Internal method dispatcher"""
        self.onInit() ### kept for compatibility
        self._onBegin()
        args = self._call_args
        kwargs = self._call_kwargs
        result = self._call_handler(*args, **kwargs) 
        self._onEnd()
        return result
        
    def _rpcDispatcher(self, method=None, mode='bag', **kwargs):
        parameters = self.site.parse_kwargs(kwargs, workdate=self.workdate)
        self._lastUserEventTs = parameters.pop('_lastUserEventTs', None)
        self.site.handle_clientchanges(self.page_id, parameters)
        auth = AUTH_OK
        if not method in ('doLogin', 'onClosePage'):
            auth = self._checkAuth(method=method, **parameters)
        if self.isDeveloper():
            result = self.rpc(method=method, _auth=auth, **parameters)
        else:
            try:
                result = self.rpc(method=method, _auth=auth, **parameters)
            except GnrException, e:
                self.rpc.error = str(e)
                result = None
        result_handler = getattr(self.rpc, 'result_%s' % mode.lower())
        
        return_result = result_handler(result)
        return return_result
        
    def _checkAuth(self, method=None, **parameters):
        pageTags = self.pageAuthTags(method=method, **parameters)
        if not pageTags:
            return AUTH_OK
        if not self.connection.loggedUser:
            if method != 'main':
                return 'EXPIRED'
            return AUTH_NOT_LOGGED
        if not self.application.checkResourcePermission(pageTags, self.userTags):
            return AUTH_FORBIDDEN
        return AUTH_OK
        
    def mixinComponent(self, pkg, *path):
        """add???
        
        :param pkg: add???
        :param \*path: add???
        """
        self.site.resource_loader.mixinPageComponent(self, pkg, *path)
        
    @property
    def isGuest(self):
        """add???
        
        :returns: add???
        """
        return self.user == self.connection.guestname
        
    def rpc_doLogin(self, login=None, guestName=None, **kwargs):
        """Service method. Set user's avatar into its connection if:
        
            * The user exists and his password is correct.
            * The user is a guest
            
        :param login: add???. Default value is ``None``
        :param guestName: add???. Default value is ``None``
        :returns: add???
        """
        loginPars = {}
        if guestName:
            avatar = self.application.getAvatar(guestName)
        else:
            avatar = self.application.getAvatar(login['user'], password=login['password'],
                                                authenticate=True, page=self, **kwargs)
        if avatar:
            self.site.onAuthenticated(avatar)
            self.avatar = avatar
            #self.connection.change_user(user=avatar.user,user_id=avatar.user_id,user_name=avatar.user_name,
            #                            user_tags=avatar.user_tags)
            self.connection.change_user(avatar)
            
            self.setInClientData('gnr.avatar', Bag(avatar.as_dict()))
            login['message'] = ''
            loginPars = avatar.loginPars
            loginPars.update(avatar.extra_kwargs)
        else:
            login['message'] = 'invalid login'
        return (login, loginPars)
        
    def onInit(self):
        """add???"""
        # subclass hook
        pass
        
    def onIniting(self, request_args, request_kwargs):
        """Callback onIniting called in early stages of page initialization
        
        :param request_args: add???
        :param request_kwargs: add???
        """
        pass
        
    def onSaving(self, recordCluster, recordClusterAttr, resultAttr=None):
        """add???
        
        :param recordCluster: add???
        :param recordClusterAttr: add???
        :param resultAttr: add???. Default value is ``None``
        """
        pass
        
    def onSaved(self, record, resultAttr=None, **kwargs):
        """add???
        
        :param record: add???
        :param resultAttr: add???. Default value is ``None``
        """
        pass
        
    def onDeleting(self, recordCluster, recordClusterAttr):
        """add???
        
        :param recordCluster: add???
        :param recordClusterAttr: add???
        """
        pass
        
    def onDeleted(self, record):
        """add???
        
        :param record: add???
        """
        pass
        
    def onBegin(self):
        """add???"""
        pass
        
    def _onBegin(self):
        self.onBegin()
        self._publish_event('onBegin')
        
    def onEnd(self):
        """add???"""
        pass
        
    def getService(self, service_type):
        """add???
        
        :param service_type: add???
        :returns: add???
        """
        return self.site.getService(service_type)
        
    def _onEnd(self):
        self._publish_event('onEnd')
        self.onEnd()
        
    def collectClientDatachanges(self):
        """add???
        
        :returns: add???
        """
        self._publish_event('onCollectDatachanges')
        result = self.site.get_datachanges(self.page_id, user=self.user,
                                           local_datachanges=self.local_datachanges)
        return result
        
    def _subscribe_event(self, event, caller):
        assert hasattr(caller, 'event_%s' % event)
        self._event_subscribers.setdefault(event, []).append(caller)
        
    def _publish_event(self, event):
        for subscriber in self._event_subscribers.get(event, []):
            getattr(subscriber, 'event_%s' % event)()
            
    def rootPage(self, **kwargs):
        """add???
        
        :returns: add???
        """
        self.charset = 'utf-8'
        arg_dict = self.build_arg_dict(**kwargs)
        tpl = self.pagetemplate
        if not isinstance(tpl, basestring):
            tpl = '%s.%s' % (self.pagename, 'tpl')
        lookup = TemplateLookup(directories=self.tpldirectories, output_encoding=self.charset,
                                encoding_errors='replace')
        try:
            mytemplate = lookup.get_template(tpl)
        except:
            raise GnrWebPageException("No template %s found in %s" % (tpl, str(self.tpldirectories)))
        self.htmlHeaders()
        return mytemplate.render(mainpage=self, **arg_dict)
        
    def _set_locale(self, val):
        self._locale = val
        
    def _get_locale(self): # TODO IMPLEMENT DEFAULT FROM APP OR AVATAR 
        if not hasattr(self, '_locale'):
            self._locale = self.connection.locale or self.request.headers.get('Accept-Language', 'en').split(',')[
                                                     0] or 'en'
        return self._locale
        
    locale = property(_get_locale, _set_locale)
        
    def rpc_changeLocale(self, locale):
        """add???
        
        :param locale: add???
        """
        self.connection.locale = locale.lower()
        
    def toText(self, obj, locale=None, format=None, mask=None, encoding=None, dtype=None):
        """add???
        
        :param obj: add???
        :param locale: add???. Default value is ``None``
        :param format: add???. Default value is ``None``
        :param mask: add???. Default value is ``None``
        :param encoding: add???. Default value is ``None``
        :param dtype: add???. Default value is ``None``
        :returns: add???
        """
        locale = locale or self.locale
        return toText(obj, locale=locale, format=format, mask=mask, encoding=encoding)
        
    def getUuid(self):
        """add???
        
        :returns: add???
        """
        return getUuid()
        
    def addHtmlHeader(self, tag, innerHtml='', **kwargs):
        """add???
        
        :param tag: add???
        :param innerHtml: add???. Default value is ``''``
        """
        attrString = ' '.join(['%s="%s"' % (k, str(v)) for k, v in kwargs.items()])
        self._htmlHeaders.append('<%s %s>%s</%s>' % (tag, attrString, innerHtml, tag))
        
    def htmlHeaders(self):
        """add???"""
        pass
        
    def _get_pageArgs(self):
        return self.pageStore().getItem('pageArgs') or {}
        
    pageArgs = property(_get_pageArgs)
        
    def _(self, txt):
        if txt.startswith('!!'):
            txt = self.localizer.translateText(txt[2:])
        return txt
        
    def getPublicMethod(self, prefix, method):
        """add???
        
        :param prefix: add???
        :param method: add???
        :returns: add???
        """
        handler = None
        if '.' in method:
            proxy_name, submethod = method.split('.', 1)
            proxy_object = getattr(self, proxy_name, None)
            if not proxy_object:
                proxy_class = self.pluginhandler.get_plugin(proxy_name)
                proxy_object = proxy_class(self)
            if proxy_object:
                handler = getattr(proxy_object, '%s_%s' % (prefix, submethod), None)
        else:
            handler = getattr(self, '%s_%s' % (prefix, method))
        return handler
        
    def build_arg_dict(self, **kwargs):
        """add???
        
        :returns: add???
        """
        gnr_static_handler = self.site.getStatic('gnr')
        gnrModulePath = gnr_static_handler.url(self.gnrjsversion)
        arg_dict = {}
        self.frontend.frontend_arg_dict(arg_dict)
        arg_dict['customHeaders'] = self._htmlHeaders
        arg_dict['charset'] = self.charset
        arg_dict['filename'] = self.pagename
        arg_dict['pageMode'] = 'wsgi_10'
        arg_dict['baseUrl'] = self.site.home_uri
        if self.debugopt:
            kwargs['debugopt'] = self.debugopt
        if self.isDeveloper:
            kwargs['isDeveloper'] = True
        arg_dict['startArgs'] = toJson(kwargs)
        arg_dict['page_id'] = self.page_id or getUuid()
        arg_dict['bodyclasses'] = self.get_bodyclasses()
        arg_dict['gnrModulePath'] = gnrModulePath
        gnrimports = self.frontend.gnrjs_frontend()
        if self.site.debug or self.isDeveloper():
            arg_dict['genroJsImport'] = [self.mtimeurl(self.gnrjsversion, 'js', '%s.js' % f) for f in gnrimports]
        elif self.site.config['closure_compiler']:
            jsfiles = [gnr_static_handler.path(self.gnrjsversion, 'js', '%s.js' % f) for f in gnrimports]
            arg_dict['genroJsImport'] = [self.jstools.closurecompile(jsfiles)]
        else:
            jsfiles = [gnr_static_handler.path(self.gnrjsversion, 'js', '%s.js' % f) for f in gnrimports]
            arg_dict['genroJsImport'] = [self.jstools.compress(jsfiles)]
        arg_dict['css_genro'] = self.get_css_genro()
        arg_dict['js_requires'] = [x for x in [self.getResourceUri(r, 'js', add_mtime=True) for r in self.js_requires]
                                   if x]
        css_path, css_media_path = self.get_css_path()
        arg_dict['css_requires'] = css_path
        arg_dict['css_media_requires'] = css_media_path
        return arg_dict
        
    def mtimeurl(self, *args):
        """add???
        
        :returns: add???
        """
        gnr_static_handler = self.site.getStatic('gnr')
        fpath = gnr_static_handler.path(*args)
        mtime = os.stat(fpath).st_mtime
        url = gnr_static_handler.url(*args)
        url = '%s?mtime=%0.0f' % (url, mtime)
        return url
        
    def homeUrl(self):
        """add???
        
        :returns: add???
        """
        return self.site.home_uri
        
    def packageUrl(self, *args, **kwargs):
        """add???
        
        :returns: add???
        """
        pkg = kwargs.get('pkg', self.packageId)
        return self.site.pkg_page_url(pkg, *args)
        
    def getDomainUrl(self, path='', **kwargs):
        """add???
        
        :param path: add???. Default value is ``''``
        :returns: add???
        """
        params = urllib.urlencode(kwargs)
        path = '%s/%s' % (self.site.home_uri.rstrip('/'), path.lstrip('/'))
        if params:
            path = '%s?%s' % (path, params)
        return path
        
    def externalUrl(self, path, **kwargs):
        """add???
        
        :param path: add???. Default value is ``''``
        :returns: add???
        """
        params = urllib.urlencode(kwargs)
        #path = os.path.join(self.homeUrl(), path)
        if path == '': path = self.siteUri
        path = self._request.relative_url(path)
        if params:
            path = '%s?%s' % (path, params)
        return path
        
    def externalUrlToken(self, path, _expiry=None, _host=None, method='root', **kwargs):
        """add???
        
        :param path: add???
        :param _expiry: add???. Default value is ``None``
        :param _host: add???. Default value is ``None``
        :param method: add???. Default value is ``root``
        :returns: add???
        """
        assert 'sys' in self.site.gnrapp.packages
        external_token = self.db.table('sys.external_token').create_token(path, expiry=_expiry, allowed_host=_host,
                                                                          method=method, parameters=kwargs,
                                                                          exec_user=self.user)
        return self.externalUrl(path, gnrtoken=external_token)
        
    def get_bodyclasses(self):   #  ancora necessario _common_d11?
        """add???
        
        :returns: add???
        """
        return '%s _common_d11 pkg_%s page_%s %s' % (
        self.frontend.theme or '', self.packageId, self.pagename, getattr(self, 'bodyclasses', ''))
        
    def get_css_genro(self):
        """add???
        
        :returns: add???
        """
        css_genro = self.frontend.css_genro_frontend()
        for media in css_genro.keys():
            css_genro[media] = [self.mtimeurl(self.gnrjsversion, 'css', '%s.css' % f) for f in css_genro[media]]
        return css_genro
        
    def _get_domSrcFactory(self):
        return self.frontend.domSrcFactory
        
    domSrcFactory = property(_get_domSrcFactory)
        
    def newSourceRoot(self):
        """add???
        
        :returns: add???
        """
        return self.domSrcFactory.makeRoot(self)
        
    def newGridStruct(self, maintable=None):
        """Allow to create a Grid Struct.
        
        :param maintable: the table to which the struct refers to. For more information,
                          check the :ref:`webpages_maintable` section. Default value is ``None``
        :returns: the Grid Struct
        """
        return GnrGridStruct.makeRoot(self, maintable=maintable)
        
    def _get_folders(self):
        return {'pages': self.site.pages_dir,
                'site': self.site.site_path,
                'current': os.path.dirname(self.filepath)}
                
    def pageStore(self, page_id=None, triggered=True):
        """add???
        
        :param page_id: add???. Deafult value is ``None``
        :param triggered: boolean. add???. Deafult value is ``True``
        :returns: add???
        """
        page_id = page_id or self.page_id
        return self.site.register.pageStore(page_id, triggered=triggered)
        
    def connectionStore(self, connection_id=None, triggered=True):
        """add???
        
        :param connection_id: add???. Default value is ``None``
        :param triggered: boolean. add???. Default value is ``True``
        :returns: add???
        """
        connection_id = connection_id or self.connection_id
        return self.site.register.connectionStore(connection_id, triggered=triggered)
        
    def userStore(self, user=None, triggered=True):
        """add???
        
        :param user: add???. Default value is ``None``
        :param triggered: boolean. add???. Default value is ``True``
        :returns: add???
        """
        user = user or self.user
        return self.site.register.userStore(user, triggered=triggered)
        
    def rpc_setStoreSubscription(self, storename=None, client_path=None, active=True):
        """add???
        
        :param storename: add???. Default value is ``None``
        :param client_path: add???. Default value is ``None``
        :param active: boolean. add???. Default value is ``True``
        """
        with self.pageStore() as store:
            subscriptions = store.getItem('_subscriptions')
            if subscriptions is None:
                subscriptions = dict()
                store.setItem('_subscriptions', subscriptions)
            storesub = subscriptions.setdefault(storename, {})
            pathsub = storesub.setdefault(client_path, {})
            pathsub['on'] = active
            
    def clientPage(self, page_id=None):
        """add???
        
        :param page_id: add???. Default value is ``None``
        :returns: add???
        """
        return ClientPageHandler(self, page_id or self.page_id)
        
    def _get_pkgapp(self):
        if not hasattr(self, '_pkgapp'):
            self._pkgapp = self.site.gnrapp.packages[self.packageId]
        return self._pkgapp
        
    pkgapp = property(_get_pkgapp)
        
    def _get_sitepath(self):
        return self.site.site_path
        
    sitepath = property(_get_sitepath)
        
    def _get_siteUri(self):
        return self.site.home_uri
        
    siteUri = property(_get_siteUri)
        
    def _get_parentdirpath(self):
        try:
            return self._parentdirpath
        except AttributeError:
            self._parentdirpath = self.resolvePath()
            return self._parentdirpath
            
    parentdirpath = property(_get_parentdirpath)
        
    @property
    def subscribedTablesDict(self):
        """Return a dict of subscribed tables. Every element is a list
           of *page_id*\'s that subscribe that page"""
        if not hasattr(self, '_subscribedTablesDict'):
            self._subscribedTablesDict = self.db.table('adm.served_page').subscribedTablesDict()
        return self._subscribedTablesDict
        
    @property
    def application(self):
        """add???"""
        return self.site.gnrapp
        
    @property
    def app(self):
        """add???"""
        if not hasattr(self, '_app'):
            self._app = GnrWebAppHandler(self)
        return self._app
        
    @property
    def btc(self):
        """add???"""
        if not hasattr(self, '_btc'):
            self._btc = GnrWebBatch(self)
        return self._btc
        
    @property
    def catalog(self):
        """add???"""
        return self.application.catalog
        
    @property
    def userTags(self):
        """add???"""
        return self.connection.user_tags
        
    @property
    def user(self):
        """add???"""
        return self.connection.user
        
    @property
    def connection_id(self):
        """add???"""
        return self.connection.connection_id
        
    def _set_avatar(self, avatar):
        self._avatar = avatar
        
    def _get_avatar(self):
        if self.isGuest:
            return
        if not hasattr(self, '_avatar'):
            connection = self.connection
            avatar_extra = connection.avatar_extra or dict()
            self._avatar = self.application.getAvatar(self.user, tags=connection.user_tags, page=self,
                                                      **avatar_extra)
        return self._avatar
        
    avatar = property(_get_avatar, _set_avatar)
        
    def checkPermission(self, pagepath, relative=True):
        """add???
        
        :param pagepath: add???
        :param relative: add???. Default value is ``True``
        :returns: add???
        """
        return self.application.checkResourcePermission(self.auth_tags, self.userTags)
        
    def get_css_theme(self):
        """Get the css_theme. The css_theme get is the one defined the :ref:`siteconfig_gui` tag of
        your :ref:`sites_siteconfig` or in a single :ref:`webpages_webpages` through the
        :ref:`webpages_css_theme` webpage variable
        
        :returns: the css theme
        """
        return self.css_theme
        
    def get_css_path(self, requires=None):
        """Get the css path included in the :ref:`webpages_css_requires`.
        
        :param requires: If None, get the css_requires string included in a :ref:`webpages_webpages`
        :returns: add???
        """
        requires = [r for r in (requires or self.css_requires) if r]
        css_theme = self.get_css_theme()
        if css_theme:
            requires.append('themes/%s' % self.css_theme)
        self.onServingCss(requires)
        #requires.reverse()
        filepath = os.path.splitext(self.filepath)[0]
        css_requires = []
        css_media_requires = {}
        for css in requires:
            if ':' in css:
                css, media = css.split(':')
            else:
                media = None
            csslist = self.site.resource_loader.getResourceList(self.resourceDirs, css, 'css')
            if csslist:
                #csslist.reverse()
                css_uri_list = [self.getResourceUri(css, add_mtime=True) for css in csslist]
                if media:
                    css_media_requires.setdefault(media, []).extend(css_uri_list)
                else:
                    css_requires.extend(css_uri_list)
        if os.path.isfile('%s.css' % filepath):
            css_requires.append(self.getResourceUri('%s.css' % filepath, add_mtime=True))
        if os.path.isfile(self.resolvePath('%s.css' % self.pagename)):
            css_requires.append('%s.css' % self.pagename)
        return css_requires, css_media_requires

    def getResourceList(self, path, ext=None):
        return self.site.resource_loader.getResourceList(self.resourceDirs, path, ext=ext)

    def getResourceUriList(self, path, ext=None, add_mtime=False):
        flist = self.getResourceList(path, ext=ext)
        return [self.resolveResourceUri(f, add_mtime=add_mtime) for f in flist]

    def getResourceExternalUriList(self,path, ext=None, add_mtime=False):
        flist = self.getResourceList(path, ext=ext)
        return [self.externalUrl(self.resolveResourceUri(f, add_mtime=add_mtime)) for f in flist]

    def onServingCss(self, css_requires):
        """add???
        
        :param css_requires: add???
        """
        pass
        
    def getResourceUri(self, path, ext=None, add_mtime=False):
        fpath = self.getResource(path, ext=ext)
        if not fpath:
            return
        return self.resolveResourceUri(fpath, add_mtime=add_mtime)


    def resolveResourceUri(self, fpath, add_mtime=False):
        url = None
        if fpath.startswith(self.site.site_path):
            uripath = fpath[len(self.site.site_path):].lstrip('/').split(os.path.sep)
            url = self.site.getStatic('site').url(*uripath)
        elif fpath.startswith(self.site.pages_dir):
            uripath = fpath[len(self.site.pages_dir):].lstrip('/').split(os.path.sep)
            url = self.site.getStatic('pages').url(*uripath)
        elif fpath.startswith(self.package_folder):
            uripath = fpath[len(self.package_folder):].lstrip('/').split(os.path.sep)
            url = self.site.getStatic('pkg').url(self.packageId, *uripath)
        else:
            for rsrc, rsrc_path in self.site.resources.items():
                if fpath.startswith(rsrc_path):
                    uripath = fpath[len(rsrc_path):].lstrip('/').split(os.path.sep)
                    url = self.site.getStatic('rsrc').url(rsrc, *uripath)
                    break
        if url and add_mtime:
            mtime = os.stat(fpath).st_mtime
            url = '%s?mtime=%0.0f' % (url, mtime)
        return url
        
    def getResource(self, path, ext=None):
        result = self.site.resource_loader.getResourceList(self.resourceDirs, path, ext=ext)
        if result:
            return result[0]
            
    def setPreference(self, path, data, pkg=''):
        self.site.setPreference(path, data, pkg=pkg)
        
    def getPreference(self, path, pkg='', dflt=''):
        return self.site.getPreference(path, pkg=pkg, dflt=dflt)
        
    def getUserPreference(self, path, pkg='', dflt='', username=''):
        return self.site.getUserPreference(path, pkg=pkg, dflt=dflt, username=username)
        
    def rpc_getUserPreference(self, path='*'):
        return self.getUserPreference(path)
        
    def rpc_getAppPreference(self, path='*'):
        return self.getPreference(path)
        
    def setUserPreference(self, path, data, pkg='', username=''):
        self.site.setUserPreference(path, data, pkg=pkg, username=username)
        
    def setInClientData(self, path, value=None, attributes=None, page_id=None, filters=None,
                        fired=False, reason=None, public=False, replace=False):
        if filters:
            pages = self.site.register.pages(filters=filters)
        else:
            pages = [page_id]
        for page_id in pages:
            if not public and (page_id is None or page_id == self.page_id):
                if isinstance(path, Bag):
                    changeBag = path
                    for changeNode in changeBag:
                        attr = changeNode.attr
                        datachange = ClientDataChange(attr.pop('_client_path'), changeNode.value,
                                                      attributes=attr, fired=attr.pop('fired', None))
                        self.local_datachanges.append(datachange)
                else:
                    datachange = ClientDataChange(path, value, reason=reason, attributes=attributes, fired=fired)
                    self.local_datachanges.append(datachange)
            else:
                with self.clientPage(page_id=page_id) as clientPage:
                    clientPage.set(path, value, attributes=attributes, reason=reason, fired=fired)
                    
    def rpc_sendMessageToClient(self, message, pageId=None, filters=None, msg_path=None):
        self.site.sendMessageToClient(message, pageId=pageId, filters=filters, origin=self, msg_path=msg_path)
        
    def _get_package_folder(self):
        if not hasattr(self, '_package_folder'):
            self._package_folder = os.path.join(self.site.gnrapp.packages[self.packageId].packageFolder, 'webpages')
        return self._package_folder
        
    package_folder = property(_get_package_folder)
        
    def rpc_main(self, _auth=AUTH_OK, debugger=None, **kwargs):
        page = self.domSrcFactory.makeRoot(self)
        self._root = page
        pageattr = {}
        #try :
        if True:
            if _auth == AUTH_OK:
                avatar = self.avatar #force get_avatar
                if hasattr(self, 'main_root'):
                    self.main_root(page, **kwargs)
                    return (page, pageattr)
                    #page.script('genro.dom.windowTitle("%s")' % self.windowTitle())
                dbselect_cache = None
                if self.user:
                    dbselect_cache = self.getUserPreference(path='cache.dbselect', pkg='sys')
                if dbselect_cache is None:
                    dbselect_cache = self.site.config['client_cache?dbselect']
                if dbselect_cache:
                    page.script('genro.cache_dbselect = true')
                page.data('gnr.windowTitle', self.windowTitle())
                page.data('gnr.homepage', self.externalUrl(self.site.homepage))
                page.data('gnr.homeFolder', self.externalUrl(self.site.home_uri).rstrip('/'))
                page.data('gnr.homeUrl', self.site.home_uri)
                #page.data('gnr.userTags', self.userTags)
                page.data('gnr.locale', self.locale)
                page.data('gnr.pagename', self.pagename)
                if not self.isGuest:
                    page.dataRemote('gnr.user_preference', 'getUserPreference')
                page.dataRemote('gnr.app_preference', 'getAppPreference')
                page.dataController('genro.dlg.serverMessage("gnr.servermsg");', _fired='^gnr.servermsg')
                page.dataController("genro.getDataNode(nodePath).refresh(true);",
                                    nodePath="^gnr.serverEvent.refreshNode")

                page.dataController('if(url){genro.download(url)};', url='^gnr.downloadurl')
                page.dataController("""if(url){
                                        genro.download(url,null,"print")
                                        };""", url='^gnr.printurl')

                page.dataController('console.log(msg);funcCreate(msg)();', msg='^gnr.servercode')

                root = page.borderContainer(design='sidebar', height='100%', nodeId='_gnrRoot',
                                            _class='hideSplitter notvisible',
                                            regions='^_clientCtx.mainBC')
                typekit_code = self.site.config['gui?typekit']
                if typekit_code:
                    page.script(src="http://use.typekit.com/%s.js" % typekit_code)
                    page.dataController("try{Typekit.load();}catch(e){}", _onStart=True)
                #self.debugger.right_pane(root)
                #self.debugger.bottom_pane(root)
                self.mainLeftContent(root, region='left', splitter=True, nodeId='gnr_main_left')
                root.div(_class='trash_drop', dropTarget=True, dropTypes='trashable', id='trash_drop',
                         onDrop_trashable="""var sourceNode=genro.src.nodeBySourceNodeId(dropInfo.dragSourceInfo._id);
                                            if(sourceNode&&sourceNode.attr.onTrashed){
                                                funcCreate(sourceNode.attr.onTrashed,'data,dropInfo',sourceNode)(data,dropInfo);
                                            }""")
                root.div(id='auxDragImage')
                root.div(id='srcHighlighter')
                root.dataController("""
                                       var new_status = main_left_set_status[0];
                                       new_status = new_status=='toggle'? !current_status:new_status;
                                       if(new_status!=current_status){
                                    
                                            SET _clientCtx.mainBC.left?show=new_status;
                                            left_width = left_width || '';
                                            if(new_status && left_width.replace('px','')<200){
                                                SET _clientCtx.mainBC.left = '200px';
                                            }
                                            PUBLISH main_left_status = new_status;
                                       }
                                    """, subscribe_main_left_set_status=True,
                                    current_status='=_clientCtx.mainBC.left?show', left_width='=_clientCtx.mainBC.left')

                rootwdg = self.rootWidget(root, region='center', nodeId='_pageRoot')
                self.main(rootwdg, **kwargs)
                self.onMainCalls()
                if self.avatar:
                    page.data('gnr.avatar', Bag(self.avatar.as_dict()))
                page.data('gnr.polling.user_polling', self.user_polling)
                page.data('gnr.polling.auto_polling', self.auto_polling)

                page.dataController("""genro.user_polling = user_polling;
                                       genro.auto_polling = auto_polling;
                                      """,
                                    user_polling="^gnr.polling.user_polling",
                                    auto_polling="^gnr.polling.auto_polling",
                                    _onStart=True)

                if self._pendingContextToCreate:
                    self._createContext(root, self._pendingContextToCreate)
                if self.user:
                    self.site.pageLog('open')

            elif _auth == AUTH_NOT_LOGGED:
                loginUrl = self.application.loginUrl()
                if not loginUrl.startswith('/'):
                    loginUrl = self.site.home_uri + loginUrl
                page = None
                if loginUrl:
                    pageattr['redirect'] = loginUrl
                else:
                    pageattr['redirect'] = self.resolvePathAsUrl('simplelogin.py', folder='*common')
            else:
                self.forbiddenPage(page, **kwargs)
            return (page, pageattr)
            #except Exception,err:
        else:
            return (self._errorPage(err), pageattr)
            
    def onMain(self): #You CAN override this !
        pass
            
    def mainLeftTop(self, pane):
        pass
            
    def mainLeftContent(self, parentBC, **kwargs):
        plugin_list = getattr(self, 'plugin_list', None)
        if not plugin_list:
            return
        bc = parentBC.borderContainer(_class='main_left_tab', width='200px', datapath='gnr.main_container.left',
                                      **kwargs)
        self.mainLeftTop(bc.contentPane(region='top', nodeId='gnr_main_left_bottom', id='gnr_main_left_top'))
        bottom = bc.contentPane(region='bottom', nodeId='gnr_main_left_bottom', id='gnr_main_left_bottom',
                                overflow='hidden')
        plugin_dock = bottom.slotBar(slots='*,%s,*' %self.plugin_list)
        sc = bc.stackContainer(selectedPage='^.selected', region='center', nodeId='gnr_main_left_center')
        sc.dataController("""genro.publish(page+'_'+(selected?'on':'off'));
                             genro.dom.setClass(genro.domById('plugin_block_'+page),'selected_plugin',selected);
                            """,
                          subscribe_gnr_main_left_center_selected=True)

        sc.dataController("""
                            var command= main_left_status[0]?'open':'close';
                            genro.publish(page+'_'+(command=='open'?'on':'off'));
                            """,
                          subscribe_main_left_status=True,
                          page='=.selected')

        for plugin in self.plugin_list.split(','):
            cb = getattr(self, 'mainLeft_%s' % plugin)
            assert cb, 'Plugin %s not found' % plugin
            cb(sc.contentPane(pageName=plugin))
            sc.dataController("""
                            PUBLISH main_left_set_status = true;
                            SET .selected=plugin;
                          """, **{'subscribe_%s_open' % plugin: True, 'plugin': plugin})

            getattr(plugin_dock,plugin).div(_class='plugin_block %s_icon' % plugin,
                                            connect_onclick="""SET .selected="%s";""" % plugin,
                                            id='plugin_block_%s' % plugin)

    def onMainCalls(self):
        calls = [m for m in dir(self) if m.startswith('onMain_')]
        for m in calls:
            getattr(self, m)()
        self.onMain()

    def rpc_onClosePage(self, **kwargs):
        self.site.onClosePage(self)
        #self.pageFolderRemove()

    def pageFolderRemove(self):
        shutil.rmtree(os.path.join(self.connectionFolder, self.page_id), True)

    def rpc_callTableScript(self, table=None, respath=None, class_name='Main', downloadAs=None, **kwargs):
        """Call a script from a table's resources (i.e. ``_resources/tables/<table>/<respath>``).
        
        This is typically used to customize prints and batch jobs for a particular installation.
        """
        if downloadAs:
            import mimetypes

            self.response.content_type = mimetypes.guess_type(downloadAs)[0]
            self.response.add_header("Content-Disposition", str("attachment; filename=%s" % downloadAs))
        return self.site.callTableScript(page=self, table=table, respath=respath, class_name=class_name,
                                         downloadAs=downloadAs, **kwargs)

    def rpc_remoteBuilder(self, handler=None, **kwargs):
        handler = self.getPublicMethod('remote', handler)
        if handler:
            pane = self.newSourceRoot()
            self._root = pane
            for k, v in kwargs.items():
                if k.endswith('_path'):
                    kwargs[k[0:-5]] = kwargs.pop(k)[1:]
            handler(pane, **kwargs)
            return pane

    def rpc_ping(self, **kwargs):
        pass

    def rpc_setInServer(self, path, value=None, pageId=None, **kwargs):
        with self.pageStore(pageId) as store:
            store.setItem(path, value)

   #def rpc_setViewColumns(self, contextTable=None, gridId=None, relation_path=None, contextName=None,
   #                       query_columns=None, **kwargs):
   #    self.app.setContextJoinColumns(table=contextTable, contextName=contextName, reason=gridId,
   #                                   path=relation_path, columns=query_columns)

    def rpc_getPrinters(self):
        print_handler = self.getService('print')
        if print_handler:
            return print_handler.getPrinters()

    def rpc_getPrinterAttributes(self, printer_name):
        if printer_name and printer_name != 'PDF':
            attributes = self.getService('print').getPrinterAttributes(printer_name)
            return attributes

    def rpc_relationExplorer(self, table=None, prevRelation='', prevCaption='',
                             omit='', **kwargs):
        if not table:
            return Bag()

        def buildLinkResolver(node, prevRelation, prevCaption):
            nodeattr = node.getAttr()
            if not 'name_long' in nodeattr:
                raise Exception(nodeattr) # FIXME: use a specific exception class
            nodeattr['caption'] = nodeattr.pop('name_long')
            nodeattr['fullcaption'] = concat(prevCaption, self._(nodeattr['caption']), '/')
            if nodeattr.get('one_relation'):
                nodeattr['_T'] = 'JS'
                if nodeattr['mode'] == 'O':
                    relpkg, reltbl, relfld = nodeattr['one_relation'].split('.')
                else:
                    relpkg, reltbl, relfld = nodeattr['many_relation'].split('.')
                jsresolver = "genro.rpc.remoteResolver('relationExplorer',{table:%s, prevRelation:%s, prevCaption:%s, omit:%s})"
                node.setValue(jsresolver % (
                jsquote("%s.%s" % (relpkg, reltbl)), jsquote(concat(prevRelation, node.label)),
                jsquote(nodeattr['fullcaption']), jsquote(omit)))

        result = self.db.relationExplorer(table=table,
                                          prevRelation=prevRelation,
                                          omit=omit,
                                          **kwargs)
        result.walk(buildLinkResolver, prevRelation=prevRelation, prevCaption=prevCaption)
        return result

    def rpc_setInClientPage(self, pageId=None, changepath=None, value=None, fired=None, attr=None, reason=None):
        with self.clientPage(pageId) as clientPage:
            clientPage.set(changepath, value, attr=attr, reason=reason, fired=fired)

    def getAuxInstance(self, name):
        return self.site.getAuxInstance(name)

    def _get_connectionFolder(self):
        return os.path.join(self.site.allConnectionsFolder, self.connection_id)

    connectionFolder = property(_get_connectionFolder)

    def _get_userFolder(self):
        user = self.user or 'Anonymous'
        return os.path.join(self.site.allUsersFolder, user)

    userFolder = property(_get_userFolder)

    def temporaryDocument(self, *args):
        return self.connectionDocument('temp', *args)

    def temporaryDocumentUrl(self, *args, **kwargs):
        return self.connectionDocumentUrl('temp', *args, **kwargs)


    def connectionDocument(self, *args):
        filepath = os.path.join(self.connectionFolder, self.page_id, *args)
        folder = os.path.dirname(filepath)
        if not os.path.isdir(folder):
            os.makedirs(folder)
        return filepath

    def userDocument(self, *args):
        filepath = os.path.join(self.userFolder, *args)
        folder = os.path.dirname(filepath)
        if not os.path.isdir(folder):
            os.makedirs(folder)
        return filepath

    def connectionDocumentUrl(self, *args, **kwargs):
        if kwargs:
            return self.site.getStatic('conn').kwargs_url(self.connection_id, self.page_id, *args, **kwargs)
        else:
            return self.site.getStatic('conn').url(self.connection_id, self.page_id, *args)

    def userDocumentUrl(self, *args, **kwargs):
        if kwargs:
            return self.site.getStatic('user').kwargs_url(self.user, *args, **kwargs_url)
        else:
            return self.site.getStatic('user').url(self.user, *args)

    def isLocalizer(self):
        return (self.userTags and ('_TRD_' in self.userTags))

    def isDeveloper(self):
        return (self.userTags and ('_DEV_' in self.userTags))

    def addToContext(self, value=None, serverpath=None, clientpath=None):
        self._pendingContextToCreate.append((value, serverpath, clientpath or serverpath))

    def _createContext(self, root, pendingContext):
        with self.pageStore() as store:
            for value, serverpath, clientpath in pendingContext:
                store.setItem(serverpath, value)
        for value, serverpath, clientpath in pendingContext:
            root.child('data', __cls='bag', content=value, path=clientpath, _serverpath=serverpath)

    def setJoinCondition(self, ctxname, target_fld='*', from_fld='*', condition=None, one_one=None, applymethod=None,
                         **kwargs):
        """define join condition in a given context (ctxname)
           the condition is used to limit the automatic selection of related records
           If target_fld AND from_fld equals to '*' the condition is an additional where clause added to any selection
           
           self.setJoinCondition('mycontext',
                              target_fld = 'mypkg.rows.document_id',
                              from_fld = 'mypkg.document.id',
                              condition = "mypkg.rows.date <= :join_wkd",
                              join_wkd = "^mydatacontext.foo.bar.mydate", one_one=False)
                              
            @param ctxname: name of the context of the main record 
            @param target_fld: the many table column of the relation, '*' means the main table of the selection
            @param from_fld: the one table column of the relation, '*' means the main table of the selection
            @param condition: the sql condition
            @param one_one: the result is returned as a record instead of as a selection. 
                            If one_one is True the given condition MUST return always a single record
            @param applymethod: a page method to be called after selecting the related records
            @param kwargs: named parameters to use in condition. Can be static values or can be readed 
                           from the context at query time. If a parameter starts with '^' it is a path in 
                           the context where the value is stored. 
                           If a parameter is the name of a defined method the method is called and the result 
                           is used as the parameter value. The method has to be defined as 'ctxname_methodname'.
        """
        path = '%s.%s_%s' % (ctxname, target_fld.replace('.', '_'), from_fld.replace('.', '_'))
        value = Bag(dict(target_fld=target_fld, from_fld=from_fld, condition=condition, one_one=one_one,
                         applymethod=applymethod, params=Bag(kwargs)))

        self.addToContext(value=value, serverpath='_sqlctx.conditions.%s' % path,
                          clientpath='gnr.sqlctx.conditions.%s' % path)

   #def setJoinColumns(self, ctxname, target_fld, from_fld, joincolumns):
   #    path = '%s.%s_%s' % (ctxname, target_fld.replace('.', '_'), from_fld.replace('.', '_'))
   #    serverpath = '_sqlctx.columns.%s' % path
   #    clientpath = 'gnr.sqlctx.columns.%s' % path
   #    self.addToContext(value=joincolumns, serverpath=serverpath, clientpath=clientpath)
        
    def _prepareGridStruct(self,source=None,table=None,gridId=None):
        struct = None
        if isinstance(source, Bag):
            return source
        if gridId and not source:
            source = getattr(self, '%s_struct' % gridId,None)
        if callable(source): 
            struct = self.newGridStruct(maintable=table)
            source(struct)
            if hasattr(struct,'_missing_table'):
                struct = None
            return struct
        if table:
            tblobj = self.db.table(table)
            if source:
                handler = getattr(tblobj, 'baseView_%s' % source,None)
                columns = handler() if handler else source
            else:
                columns= tblobj.baseViewColumns()
            struct = self.newGridStruct(maintable=table)
            rows = struct.view().rows()
            rows.fields(columns)
        return struct
        
    def rpc_getGridStruct(self,struct,table):
        return self._prepareGridStruct(struct,table)
        
    def lazyBag(self, bag, name=None, location='page:resolvers'):
        freeze_path = self.site.getStaticPath(location, name, autocreate=-1)
        bag.makePicklable()
        bag.pickle('%s.pik' % freeze_path)
        return LazyBagResolver(resolverName=name, location=location, _page=self, sourceBag=bag)

    ##### BEGIN: DEPRECATED METHODS ###
    @deprecated
    def _get_config(self):
        return self.site.config

    config = property(_get_config)

    @deprecated
    def log(self, msg):
        self.debugger.log(msg)

    ##### END: DEPRECATED METHODS #####

class LazyBagResolver(BagResolver):
    classKwargs = {'cacheTime': -1,
                   'readOnly': False,
                   'resolverName': None,
                   '_page': None,
                   'sourceBag': None,
                   'location': None,
                   'path': None,
                   'filter':None}
    classArgs = ['path']

    def load(self):
        if not self.sourceBag:
            self.getSource()
        sourceBag = self.sourceBag[self.path]
        if self.filter:

            flt,v=splitAndStrip(self.filter,'=',fixed=2)
            if  v:
                cb=lambda n: flt in n.attr and v in n.attr[flt]
            else:
                cb=lambda n: flt in n.label
            return sourceBag.filter(cb)
        result = Bag()
        for n in sourceBag:
            value = n.value
            if value and isinstance(value, Bag):
                path = n.label if not self.path else '%s.%s' % (self.path, n.label)
                value = LazyBagResolver(path=path, resolverName=self.resolverName, location=self.location)
            result.setItem(n.label, value, n.attr)
        return result
     
    def getSource(self):
        filepath = self._page.site.getStaticPath(self.location, self.resolverName)
        self.sourceBag = Bag('%s.pik' % filepath)

        
class GnrMakoPage(GnrWebPage):
    def onPreIniting(self, request_args, request_kwargs):
        request_kwargs['_plugin'] = 'mako'
        request_kwargs['mako_path'] = self.mako_template()

class ClientPageHandler(object):
    """proxi for making actions on client page"""

    def __init__(self, parent_page, page_id=None):
        self.parent_page = parent_page
        self.page_id = page_id or parent_page.page_id
        self.pageStore = self.parent_page.pageStore(page_id=self.page_id)
        self.store = None

    def set(self, path, value, attributes=None, fired=None, reason=None, replace=False):
        self.store.set_datachange(path, value, attributes=attributes, fired=fired, reason=reason, replace=replace)

    def __enter__(self):
        self.store = self.pageStore.__enter__()
        return self

    def __exit__(self, type, value, tb):
        self.pageStore.__exit__(type, value, tb)

    def jsexec(self, path, value, **kwargs):
        pass


    def copyData(self, srcpath, dstpath=None, page_id=None):
        """
        self.clientPage(page_id="nknnn").copyData('foo.bar','spam.egg') #copia sulla MIA pagina
        self.clientPage(page_id="nknnn").copyData('foo.bar','bub.egg',page_id='xxxxxx') #copia sulla  pagina xxxxxx
        self.clientPage(page_id="nknnn").copyData('foo.bar','bub.egg',pageStore=True) #copia sul mio pageStore
        self.clientPage(page_id="nknnn").copyData('foo.bar','bub.egg',page_id='xxxxxx' ,pageStore=True) #copia sul pageStore della pagina xxxx

        """
        pass

class ClientDataChange(object):
    def __init__(self, path, value, attributes=None, reason=None, fired=False,
                 change_ts=None, change_idx=None, delete=False, **kwargs):
        self.path = path
        self.reason = reason
        self.value = value
        self.attributes = attributes
        self.fired = fired
        self.change_ts = change_ts or datetime.datetime.now()
        self.change_idx = change_idx
        self.delete = delete

    def __eq__(self, other):
        return self.path == other.path and self.reason == other.reason and self.fired == other.fired

    def update(self, other):
        if hasattr(self.value, 'update') and hasattr(other.value, 'update'):
            self.value.update(other.value)
        else:
            self.value = other.value
        if other.attributes:
            self.attributes = self.attributes or dict()
            self.attributes.update(other.attributes)

    def __str__(self):
        return "Datachange path:%s, reason:%s, value:%s, attributes:%s" % (
        self.path, self.reason, self.value, self.attributes)

    def __repr__(self):
        return "Datachange path:%s, reason:%s, value:%s, attributes:%s" % (
        self.path, self.reason, self.value, self.attributes)
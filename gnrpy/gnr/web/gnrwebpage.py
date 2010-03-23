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


"""
gnrwebpage.py

Created by Giovanni Porcari on 2007-03-24.
Copyright (c) 2007 Softwell. All rights reserved.
"""
import urllib
from gnr.web._gnrbasewebpage import GnrBaseWebPage
import os
from gnr.core.gnrstring import toJson
from gnr.core.gnrlang import getUuid
from mako.lookup import TemplateLookup
from gnr.web.gnrwebreqresp import GnrWebRequest,GnrWebResponse
from gnr.web.gnrwebpage_proxy.apphandler import GnrWebAppHandler
from gnr.web.gnrwebpage_proxy.connection import GnrWebConnection
from gnr.web.gnrwebpage_proxy.rpc import GnrWebRpc
from gnr.web.gnrwebpage_proxy.session import GnrWebSession
from gnr.web.gnrwebpage_proxy.localizer import GnrWebLocalizer
from gnr.web.gnrwebpage_proxy.debugger import GnrWebDebugger
from gnr.web.gnrwebpage_proxy.utils import GnrWebUtils
from gnr.web.gnrwebpage_proxy.pluginhandler import GnrWebPluginHandler
from gnr.web.gnrwebpage_proxy.jstools import GnrWebJSTools
from gnr.web.gnrwebstruct import GnrGridStruct
from gnr.core.gnrlang import GnrGenericException, gnrImport
from gnr.core.gnrbag import Bag
from gnr.core.gnrlang import deprecated
import datetime

AUTH_OK=0
AUTH_NOT_LOGGED=1
AUTH_FORBIDDEN=-1

##### Prima di modificare le repositori Progetti
from gnr.web.gnrbaseclasses import BaseComponent

class GnrWebPageException(GnrGenericException):
    pass


class GnrWebPage(GnrBaseWebPage):
    
    
    def __init__(self, site=None, request=None, response=None, request_kwargs=None, request_args=None, filepath = None, packageId = None, basename = None):
        self.site = site
        self._event_subscribers = {}
        self._localClientDataChanges = Bag()
        self._user = None
        self.forked = False # maybe redefine as _forked
        self.page_id = request_kwargs.pop('page_id',None) or getUuid()
        self.filepath = filepath
        self.packageId = packageId
        self.basename = basename
        self.siteFolder = self.site.site_path
        self.folders= self._get_folders()
        self.called_url = request.url
        self.path_url = request.path_url
        self.request = GnrWebRequest(request)
        self.response = GnrWebResponse(response)
        self._request = self.request._request
        self._response = self.response._response
        self.response.add_header('Pragma','no-cache')
        self._htmlHeaders=[]
        self._cliCtxData = Bag()
        self.pagename = os.path.splitext(os.path.basename(self.filepath))[0].split(os.path.sep)[-1]
        self.pagepath = self.filepath.replace(self.folders['pages'], '')
        self.debug_mode = False
        self._dbconnection=None
        self._user_login = request_kwargs.pop('_user_login',None)
        self.onIniting(request_args,request_kwargs)
        
        self.private_kwargs=dict([(k[:2],v)for k,v in request_kwargs.items() if k.startswith('__')])
        self.pagetemplate = request_kwargs.pop('pagetemplate',None) or getattr(self, 'pagetemplate', None) or self.site.config['dojo?pagetemplate'] # index
        self.css_theme = request_kwargs.pop('css_theme',None) or getattr(self, 'css_theme', None) or self.site.config['gui?css_theme']
     
        self.set_call_handler(request_args, request_kwargs)
        self._call_args = request_args or tuple()
        self._call_kwargs = request_kwargs or {}
##### BEGIN: PROXY DEFINITION ########

    def _get_frontend(self):
        if not hasattr(self,'_frontend'):
            if not hasattr(self,'page_frontend') and hasattr(self,'dojoversion'):
                self.page_frontend='dojo_%s'%self.dojoversion
            frontend_module = gnrImport('gnr.web.gnrwebpage_proxy.frontend.%s'%self.page_frontend)
            frontend_class = getattr(frontend_module,'GnrWebFrontend')
            self._frontend= frontend_class(self)
        return self._frontend
    frontend = property(_get_frontend)
    
    def _get_localizer(self):
        if not hasattr(self,'_localizer'):
            self._localizer = GnrWebLocalizer(self)
        return self._localizer
    localizer = property(_get_localizer)
    
    
    def _get_debugger(self):
        if not hasattr(self,'_debugger'):
            self._debugger = GnrWebDebugger(self)
        return self._debugger
    debugger = property(_get_debugger)
    
    def _get_utils(self):
        if not hasattr(self, '_utils'):
            self._utils = GnrWebUtils(self)
        return self._utils
    utils = property(_get_utils)
    
    def _get_connection(self):
        if not hasattr(self, '_connection'):
            connection = GnrWebConnection(self)
            self._connection = connection
            connection.initConnection()
        return self._connection
    connection = property(_get_connection)

    def _get_rpc(self):
        if not hasattr(self, '_rpc'):
            self._rpc = GnrWebRpc(self)
        return self._rpc
    rpc = property(_get_rpc)
    
    def _get_session(self):
        if not hasattr(self, '_session'):
            self._session = GnrWebSession(self, lock=0)
        return self._session
    session = property(_get_session)

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
            self._db = self.app.db
            self._db.updateEnv(storename= getattr(self,'storename', None),workdate=self.workdate, locale=self.locale,
                               user=self.user, user_id=self.avatar.userid,user_tags=self.avatar.tags, pagename=self.pagename)
            for dbenv in [getattr(self,x) for x in dir(self) if x.startswith('dbenv_')]:
                kwargs=dbenv() or {}
                self._db.updateEnv( **kwargs)
        return self._db
    db = property(_get_db)
    
    def _get_workdate(self):
        if not hasattr(self,'_workdate'):
            workdate = self.pageArgs.get('_workdate_')
            if not workdate or not self.userTags or not('superadmin' in self.userTags):
                workdate =  self.session.pagedata['workdate'] or datetime.date.today()
            if isinstance(workdate, basestring):
                workdate = self.application.catalog.fromText(workdate, 'D')
            self._workdate = workdate
            self.db.workdate=workdate
        return self._workdate
    
    def _set_workdate(self, workdate):
        self.session.setInPageData('workdate', workdate)
        self.session.saveSessionData()
        self._workdate = workdate
        self.db.workdate=workdate
    workdate = property(_get_workdate, _set_workdate)
    ###### END: PROXY DEFINITION #########


    def __call__(self):
        """Internal method dispatcher"""
        self.onInit() ### kept for compatibility
        self._onBegin()
        args = self._call_args
        kwargs = self._call_kwargs
        self.debugopt=kwargs.pop('debugopt',None)
        self.callcounter=kwargs.pop('callcounter',None) or 'begin'
        if self._user_login:
            user=self.user # if we have an embedded login we get the user right now
        result = self._call_handler(*args,**kwargs)
        self._onEnd()
        return result
    
    def set_call_handler(self, request_args, request_kwargs):
        if '_plugin' in request_kwargs:
            plugin = self.pluginhandler.get_plugin(request_kwargs['_plugin'],request_args=request_args, request_kwargs=request_kwargs)
            self._call_handler=plugin
        elif 'method' in request_kwargs:
            self._call_handler=self._rpcDispatcher
        elif 'rpc' in request_kwargs:
            method = request_kwargs.pop('rpc')
            self._call_handler = self.getPublicMethod('rpc',method)
        elif 'gnrtoken' in request_kwargs:
            external_token = request_kwargs.pop('gnrtoken')
            method,token_args,token_kwargs,user = self.db.table('sys.external_token').use_token(external_token, commit=True)
            if user:
                self._user=user # TODO: refactor and cleanup
            if method:
                if method=='root':
                    self._call_handler=self.rootPage
                else:
                    self._call_handler = self.getPublicMethod('rpc',method)
                request_args.extend(token_args)
                request_kwargs.update([(str(k),v) for k,v in token_kwargs.items()])
        else:
            self._call_handler=self.rootPage
            #request_kwargs['dojo_theme']=self.dojo_theme
            request_kwargs['pagetemplate']=self.pagetemplate

    def _rpcDispatcher(self, method=None, xxcnt='', mode='bag',**kwargs):
        if False and method!= 'main':
            if self.session.pagedata['page_id']!=self.page_id :
                self.raiseUnauthorized()
        parameters = dict(kwargs)
        for k,v in kwargs.items():
            if isinstance(v, basestring):
                try:
                    v=self.catalog.fromTypedText(v, workdate=self.workdate)
                    if isinstance(v, basestring):
                        v = v.decode('utf-8')
                    parameters[k] = v
                except Exception, e:
                    raise e
        auth = AUTH_OK
        if not method in ('doLogin', 'jscompress'):
            auth = self._checkAuth(method=method, **parameters)
        
        result = self.rpc(method=method, _auth=auth, **parameters)
            
        result_handler = getattr(self.rpc, 'result_%s' % mode.lower())
        return_result = result_handler(result)
        return return_result

    def onInit(self):
        # subclass hook
        pass

    def onIniting(self, request_args, request_kwargs):
        """Callback onIniting called in early stages of page initialization"""
        pass
    
    def onSaving(self, recordCluster, recordClusterAttr, resultAttr=None):
        pass

    def onSaved(self, record, resultAttr=None, **kwargs):
        pass

    def onDeleting(self, recordCluster, recordClusterAttr):
        pass

    def onDeleted(self, record):
        pass
    
    def onBegin(self):
        pass

    def _onBegin(self):
        self.onBegin()
        self._publish_event('onBegin')
    
    def onEnd(self):
        pass

    def _onEnd(self):
        self.handleMessages()
        self._publish_event('onEnd')
        self.onEnd()
    
    def collectClientDataChanges(self):
        dataChanges = self.clientDataChanges() or Bag()
        self._publish_event('onCollectDataChanges')
        dataChanges.update(self._localClientDataChanges)
        return dataChanges
        
    def setLocalClientDataChanges(self, changeSet):
        self._localClientDataChanges.update(changeSet)
    
    def clientDataChanges(self):
        if self.session.pagedata['_clientDataChanges']:
            self.session.loadSessionData()
            result = self.session.pagedata.pop('_clientDataChanges') or Bag()
            self.session.saveSessionData()
            return result
    
    def _subscribe_event(self, event, caller):
        assert hasattr(caller,'event_%s'%event)
        self._event_subscribers.setdefault(event,[]).append(caller)
        
    def _publish_event(self,event):
        for subscriber in self._event_subscribers.get(event,[]):
            getattr(subscriber,'event_%s'%event)()

    def rootPage(self,pagetemplate=None,**kwargs):
        #self.frontend
        #self.dojo_theme = dojo_theme or 'tundra'
        self.charset='utf-8'
        tpl = pagetemplate or 'standard.tpl'
        if not isinstance(tpl, basestring):
            tpl = '%s.%s' % (self.pagename, 'tpl')
        lookup=TemplateLookup(directories=self.tpldirectories, output_encoding=self.charset, encoding_errors='replace')
        try:
            mytemplate = lookup.get_template(tpl)
        except:
            raise GnrWebPageException("No template %s found in %s" % (tpl, str(self.tpldirectories)))
        self.htmlHeaders()
        arg_dict = self.build_arg_dict(**kwargs)
        self.saveRootPageParams(kwargs)
        return mytemplate.render(mainpage=self, **arg_dict)
    
    def saveRootPageParams(self,kwargs):
        self.session.loadSessionData()
        self.session.pagedata['pageArgs'] = kwargs
        self.session.pagedata['page_id'] = self.page_id
        self.session.pagedata['connection_id'] = self.connection.connection_id
        self.session.pagedata['pagepath'] = self.pagepath
        self.session.saveSessionData()
    
    def getUuid(self):
        return getUuid()

    def addHtmlHeader(self,tag,innerHtml='',**kwargs):
        attrString=' '.join(['%s="%s"' % (k,str(v)) for k,v in kwargs.items()])
        self._htmlHeaders.append('<%s %s>%s</%s>'%(tag,attrString,innerHtml,tag))

    def htmlHeaders(self):
        pass

    
    def _(self, txt):
        if txt.startswith('!!'):
            txt = self.localizer.translateText(txt[2:])
        return txt

    def getPublicMethod(self, prefix, method):
        if '.' in method:
            proxy_name, submethod = method.split('.',1)
            proxy_object = getattr(self, proxy_name, None)
            if not proxy_object:
                proxy_class = self.pluginhandler.get_plugin(proxy_name)
                proxy_object = proxy_class(self)
            if proxy_object:
                handler = getattr(proxy_object, '%s_%s' % (prefix,submethod), None)
        else:
            handler = getattr(self, '%s_%s' % (prefix,method))
        return handler
    
    def build_arg_dict(self,**kwargs):
        gnrModulePath = self.site.gnr_static_url(self.gnrjsversion)
        arg_dict={}
        self.frontend.frontend_arg_dict(arg_dict)
        arg_dict['customHeaders']=self._htmlHeaders
        arg_dict['charset'] = self.charset
        arg_dict['filename'] = self.pagename
        arg_dict['pageMode'] = 'wsgi_10'
        arg_dict['baseUrl'] = self.site.home_uri
        if self.debugopt:
            kwargs['debugopt']=self.debugopt
        arg_dict['startArgs'] = toJson(kwargs)
        arg_dict['page_id'] = self.page_id or getUuid()
        arg_dict['bodyclasses'] = self.get_bodyclasses()
        arg_dict['gnrModulePath'] = gnrModulePath
        gnrimports = self.frontend.gnrjs_frontend()
        if self.site.debug or self.isDeveloper():
            arg_dict['genroJsImport'] = [self.mtimeurl(self.gnrjsversion,'js', '%s.js' % f) for f in gnrimports]
        elif self.site.config['closure_compiler']:
            jsfiles = [self.site.gnr_static_path(self.gnrjsversion,'js', '%s.js' % f) for f in gnrimports]
            arg_dict['genroJsImport'] = [self.jstools.closurecompile(jsfiles)]
        else:
            jsfiles = [self.site.gnr_static_path(self.gnrjsversion,'js', '%s.js' % f) for f in gnrimports]
            arg_dict['genroJsImport'] = [self.jstools.compress(jsfiles)]
        arg_dict['css_genro'] = self.get_css_genro()
        arg_dict['js_requires'] = [x for x in [self.getResourceUri(r,'js',add_mtime=True) for r in self.js_requires] if x]
        css_path, css_media_path = self.get_css_path()
        arg_dict['css_requires'] = css_path
        arg_dict['css_media_requires'] = css_media_path
        return arg_dict
    
    def mtimeurl(self, *args):
        fpath = self.site.gnr_static_path(*args)
        mtime = os.stat(fpath).st_mtime
        url = self.site.gnr_static_url(*args)
        url = '%s?mtime=%0.0f'%(url,mtime)
        return url
    
    def homeUrl(self):
        return self.site.home_uri
    
    def packageUrl(self,*args,**kwargs):
        pkg = kwargs.get('pkg',self.packageId)
        return self.site.pkg_page_url(pkg, *args)
    
    def getDomainUrl(self, path='', **kwargs):
        params = urllib.urlencode(kwargs)
        path =  '%s/%s'%(self.site.home_uri.rstrip('/'),path.lstrip('/'))
        if params:
            path = '%s?%s' % (path, params)
        return path

    def externalUrl(self, path, **kwargs):
        params = urllib.urlencode(kwargs)
        #path = os.path.join(self.homeUrl(), path)
        if path=='': path=self.siteUri
        path=self._request.relative_url(path)
        if params:
            path = '%s?%s' % (path, params)
        return path
    
    def externalUrlToken(self, path, _expiry=None,_host=None, method='root', **kwargs):
        assert 'sys' in self.site.gnrapp.packages
        external_token = self.db.table('sys.external_token').create_token(path,expiry=_expiry,allowed_host=_host,method=method,parameters=kwargs, exec_user=self.user)
        return self.externalUrl(path, gnrtoken=external_token)
    
    def get_bodyclasses(self):   #  ancora necessario _common_d11?
        return '%s _common_d11 pkg_%s page_%s %s' % (self.frontend.theme or '', self.packageId, self.pagename,getattr(self,'bodyclasses',''))
    
    def get_css_genro(self):
        css_genro = self.frontend.css_genro_frontend()
        for media in css_genro.keys():
           css_genro[media] = [self.mtimeurl(self.gnrjsversion,'css', '%s.css' % f) for f in css_genro[media]]
        return css_genro
    
    def _get_domSrcFactory(self):
        return self.frontend.domSrcFactory
    domSrcFactory = property(_get_domSrcFactory)
    
    def newSourceRoot(self):
        return self.domSrcFactory.makeRoot(self)
    
    def newGridStruct(self, maintable=None):
        return GnrGridStruct.makeRoot(self, maintable=maintable)
    
    
    def _get_folders(self):
        return {'pages':self.site.pages_dir,
                'site':self.site.site_path,
                'current':os.path.dirname(self.filepath)}
    
    def _get_app(self):
        if not hasattr(self, '_app'):
            self._app = GnrWebAppHandler(self)
        return self._app
    app = property(_get_app) #cambiare in appHandler e diminuirne l'utilizzo al minimo

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
    
    def _get_subscribedTablesDict(self):
        """return a dict of subscribed tables. any element is a list
           of page_id that subscribe that page"""
        if not hasattr (self, '_subscribedTablesDict'):
            self._subscribedTablesDict=self.db.table('adm.served_page').subscribedTablesDict()
        return self._subscribedTablesDict
    subscribedTablesDict = property(_get_subscribedTablesDict)
    
    def checkPermission(self, pagepath, relative=True):
        return self.application.checkResourcePermission(self.auth_tags, self.userTags)

    def get_css_theme(self):
        return self.css_theme
    
    def get_css_path(self, requires=None):
        requires = [r for r in (requires or self.css_requires) if r]
        css_theme = self.get_css_theme()
        if css_theme:
            requires.append('themes/%s'%self.css_theme)
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
            csslist = self.site.resource_loader.getResourceList(self.resourceDirs,css,'css')
            if csslist:
                #csslist.reverse()
                css_uri_list = [self.getResourceUri(css,add_mtime=True) for css in csslist]
                if media:
                    css_media_requires.setdefault(media,[]).extend(css_uri_list)
                else:
                    css_requires.extend(css_uri_list)
        if os.path.isfile('%s.css' % filepath):
            css_requires.append(self.getResourceUri('%s.css' % filepath,add_mtime=True))
        if os.path.isfile(self.resolvePath('%s.css' % self.pagename)):
            css_requires.append('%s.css' % self.pagename)
        return css_requires, css_media_requires
        
    def onServingCss(self, css_requires):
        pass
        
    def getResourceUri(self, path, ext=None, add_mtime=False):
        fpath=self.getResource(path, ext=ext)
        url = None
        if not fpath:
            return
        if fpath.startswith(self.site.site_path):
            uripath=fpath[len(self.site.site_path):].lstrip('/').split(os.path.sep)
            url = self.site.site_static_url(*uripath)
        elif fpath.startswith(self.site.pages_dir):
            uripath=fpath[len(self.site.pages_dir):].lstrip('/').split(os.path.sep)
            url = self.site.pages_static_url(*uripath)
        elif fpath.startswith(self.package_folder):
            uripath=fpath[len(self.package_folder):].lstrip('/').split(os.path.sep)
            url = self.site.pkg_static_url(self.packageId,*uripath)
        else:
            for rsrc,rsrc_path in self.site.resources.items():
                if fpath.startswith(rsrc_path):
                    uripath=fpath[len(rsrc_path):].lstrip('/').split(os.path.sep)
                    url = self.site.rsrc_static_url(rsrc,*uripath)
                    break
        if url and add_mtime:
            mtime = os.stat(fpath).st_mtime
            url = '%s?mtime=%0.0f'%(url,mtime)
        return url
        
    def getResource(self, path, ext=None):
        result=self.site.resource_loader.getResourceList(self.resourceDirs,path, ext=ext)
        if result:
            return result[0]
            
    def setPreference(self, path, data, pkg=''):
        self.site.setPreference(path, data,pkg=pkg)
            
    def getPreference(self,path, pkg='', dflt=''):
        return self.site.getPreference(path, pkg=pkg, dflt=dflt)
            
    def getUserPreference(self,path, pkg='',dflt='', username=''):
        return self.site.getUserPreference(path,pkg=pkg,dflt=dflt, username=username)
            
    def setUserPreference(self, path, data, pkg='',username=''):
        self.site.setUserPreference(path,data,pkg=pkg,username=username)
            
    def _get_package_folder(self):
        if not hasattr(self,'_package_folder'):
            self._package_folder = os.path.join(self.site.gnrapp.packages[self.packageId].packageFolder,'webpages')
        return self._package_folder
    package_folder = property(_get_package_folder)
    
    def rpc_main(self, _auth=AUTH_OK, debugger=None, **kwargs):
        self.connection.cookieToRefresh()
        page = self.domSrcFactory.makeRoot(self)
        self._root = page
        pageattr = {}
        #try :
        if True:
            if _auth==AUTH_OK:
                if hasattr(self,'main_root'):
                    self.main_root(page,**kwargs)
                    return (page, pageattr)
                #page.script('genro.dom.windowTitle("%s")' % self.windowTitle())
                dbselect_cache = None
                if self.user:
                    dbselect_cache = self.getUserPreference(path='cache.dbselect',pkg='sys') 
                if dbselect_cache is None:
                    dbselect_cache = self.site.config['client_cache?dbselect']
                    print 'dbselect_cache',dbselect_cache
                if dbselect_cache:
                    page.script('genro.cache_dbselect = true')
                page.data('gnr.windowTitle', self.windowTitle())
                page.data('gnr.homepage', self.externalUrl(self.site.homepage))
                page.data('gnr.homeFolder', self.externalUrl(self.site.home_uri).rstrip('/'))
                page.data('gnr.homeUrl', self.site.home_uri)
                page.data('gnr.userTags', self.userTags)
                page.data('gnr.locale',self.locale)
                page.data('gnr.pagename',self.pagename)
                page.data('gnr.polling',self.polling)
                page.data('_server', None, context='_server')
                page.dataController('genro.dlg.serverMessage(msg);', msg='^gnr.servermsg')
                page.dataController('console.log(msg);funcCreate(msg)();', msg='^gnr.servercode')
                
                page.dataController('genro.rpc.managePolling(freq);', freq='^gnr.polling', _onStart=True)
                root=page.borderContainer(design='sidebar', height='100%', nodeId='_gnrRoot',_class='hideSplitter notvisible', 
                                            regions='^_clientCtx.mainBC')
                self.debugger.right_pane(root)
                self.debugger.bottom_pane(root)
                self.mainLeftContent(root,region='left',splitter=True, nodeId='gnr_main_left')
                rootwdg = self.rootWidget(root, region='center', nodeId='_pageRoot')
                self.main(rootwdg, **kwargs)
                self.onMainCalls()
                self._createContext(root)
                if self.user:
                    self.site.pageLog('open')

            elif _auth==AUTH_NOT_LOGGED:
                loginUrl = self.application.loginUrl()
                if not loginUrl.startswith('/'):
                    loginUrl = self.site.home_uri+loginUrl
                page = None
                if loginUrl:
                    pageattr['redirect'] = loginUrl
                else:
                    pageattr['redirect'] = self.resolvePathAsUrl('simplelogin.py',folder='*common')
            else:
                self.forbiddenPage(page, **kwargs)
            return (page, pageattr)
            #except Exception,err:
        else:
            return (self._errorPage(err), pageattr)
            
    def rpc_callTableScript(self,table, respath, class_name='Main',downloadAs=None,**kwargs):
        if downloadAs:
            import mimetypes
            self.response.content_type = mimetypes.guess_type(downloadAs)[0]
            self.response.add_header("Content-Disposition",str("attachment; filename=%s"%downloadAs))
        return self.site.callTableScript(page=self, table=table, respath=respath, class_name=class_name, **kwargs)
        
    def getAuxInstance(self, name):
        return self.site.getAuxInstance(name)
        
    def _get_connectionFolder(self):
        return self.connection.connectionFolder
    connectionFolder = property(_get_connectionFolder)
 
    def temporaryDocument(self, *args):
        return self.connectionDocument('temp',*args)
    
    def temporaryDocumentUrl(self, *args):
        return self.connectionDocumentUrl('temp',*args)
        
    def connectionDocument(self, *args):
        filepath = os.path.join(self.connection.connectionFolder, self.page_id, *args)
        folder = os.path.dirname(filepath)
        if not os.path.isdir(folder):
            os.makedirs(folder)
        return filepath
    
    def connectionDocumentUrl(self, *args):
        return self.site.connection_static_url(self,*args)
    
    def isLocalizer(self) :
        return (self.userTags and ('_TRD_' in self.userTags))
        
    def isDeveloper(self) :
        return (self.userTags and ('_DEV_' in self.userTags)) 
    
    ##### BEGIN: DEPRECATED METHODS ###
    
    @deprecated
    def _get_config(self):
        return self.site.config
    config = property(_get_config)
    
    @deprecated
    def log(self, msg):
        self.debugger.log(msg)
    ##### END: DEPRECATED METHODS #####
    
class GnrMakoPage(GnrWebPage):
    
    def onIniting(self, request_args, request_kwargs):
        request_kwargs['_plugin']='mako'
        request_kwargs['path']=self.mako_template()
    
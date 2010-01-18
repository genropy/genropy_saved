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
import hashlib
import urllib
import itertools
from gnr.web._gnrbasewebpage import GnrBaseWebPage
import os
from gnr.core.gnrstring import toJson
from gnr.web.jsmin import jsmin
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
from gnr.core.gnrlang import GnrGenericException, gnrImport
from gnr.core.gnrbag import Bag
from gnr.core.gnrlang import deprecated

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
        self.onIniting(request_args,request_kwargs)
        self._user_login = request_kwargs.pop('_user_login',None)
        self.private_kwargs=dict([(k[:2],v)for k,v in request_kwargs.items() if k.startswith('__')])
        self.dojo_theme =request_kwargs.pop('dojo_theme',None) or getattr(self, 'dojo_theme', None) or self.site.config['dojo?theme'] or 'tundra'
        self.pagetemplate = request_kwargs.pop('pagetemplate',None) or getattr(self, 'pagetemplate', None) or self.site.config['dojo?pagetemplate'] # index
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
            method,token_args,token_kwargs = self.db.table('sys.external_token').use_token(external_token, commit=True)
            print token_kwargs
            if method:
                if method=='root':
                    self._call_handler=self.rootPage
                else:
                    self._call_handler = self.getPublicMethod('rpc',method)
                request_args = token_args
                request_kwargs = token_kwargs
        else:
            self._call_handler=self.rootPage
            request_kwargs['dojo_theme']=self.dojo_theme
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
            #print self.session.pagedata['_clientDataChanges']
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
    
    def rootPage(self,dojo_theme=None,pagetemplate=None,**kwargs):
        self.frontend
        self.dojo_theme = dojo_theme or 'tundra'
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
        _resources = self.site.resources.keys()
        _resources.reverse()
        dojolib = self.site.dojo_static_url(self.dojoversion,'dojo','dojo','dojo.js')
        gnrModulePath = self.site.gnr_static_url(self.gnrjsversion)
        arg_dict={}
        arg_dict['customHeaders']=self._htmlHeaders
        arg_dict['charset'] = self.charset
        arg_dict['filename'] = self.pagename
        arg_dict['pageMode'] = 'wsgi_10'
        if self.debugopt:
            kwargs['debugopt']=self.debugopt
        arg_dict['startArgs'] = toJson(kwargs)
        arg_dict['page_id'] = self.page_id or getUuid()
        arg_dict['bodyclasses'] = self.get_bodyclasses()
        arg_dict['dojolib'] = dojolib
        arg_dict['djConfig'] = "parseOnLoad: false, isDebug: %s, locale: '%s'" % (self.isDeveloper() and 'true' or 'false',self.locale)
        arg_dict['gnrModulePath'] = gnrModulePath
        gnrimports = getattr(self, '_gnrjs_d%s' % self.dojoversion)()
        if self.site.debug or self.isDeveloper():
            arg_dict['genroJsImport'] = [self.site.gnr_static_url( self.gnrjsversion,'js', '%s.js' % f) for f in gnrimports]
        elif self.site.config['closure_compiler']:
            jsfiles = [self.site.gnr_static_path(self.gnrjsversion,'js', '%s.js' % f) for f in gnrimports]
            arg_dict['genroJsImport'] = [self._jsclosurecompile(jsfiles)]
        else:
            jsfiles = [self.site.gnr_static_path(self.gnrjsversion,'js', '%s.js' % f) for f in gnrimports]
            arg_dict['genroJsImport'] = [self._jscompress(jsfiles)]
        css_dojo = getattr(self, '_css_dojo_d%s' % self.dojoversion)()
        arg_dict['css_dojo'] = [self.site.dojo_static_url(self.dojoversion,'dojo',f) for f in css_dojo]
        arg_dict['css_genro'] = self.get_css_genro()
        arg_dict['js_requires'] = [x for x in [self.getResourceUri(r,'js') for r in self.js_requires] if x]
        css_requires, css_media_requires = self.get_css_requires()
        arg_dict['css_requires'] = css_requires
        arg_dict['css_media_requires'] = css_media_requires
        return arg_dict
    
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
        external_token = self.db.table('sys.external_token').create_token(path,expiry=_expiry,allowed_host=_host,method=method,parameters=kwargs)
        return self.externalUrl(path, gnrtoken=external_token)
        
    def get_bodyclasses(self):
        return '%s _common_d11 pkg_%s page_%s %s' % (self.dojo_theme, self.packageId, self.pagename,getattr(self,'bodyclasses',''))
    
    def get_css_genro(self):
        css_genro = getattr(self, '_css_genro_d%s' % self.gnrjsversion)()
        for media in css_genro.keys():
           css_genro[media] = [self.site.gnr_static_url(self.gnrjsversion,'css', '%s.css' % f) for f in css_genro[media]]
        return css_genro
    
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
    
    def _jsclosurecompile(self, jsfiles):
        from subprocess import call
        ts = str(max([os.path.getmtime(fname) for fname in jsfiles]))
        key = '-'.join(jsfiles)
        cpfile = '%s-%s.js' % (hashlib.md5(key+ts).hexdigest(),ts)
        cppath = self.site.site_static_path('_static','_jslib', cpfile)
        jspath = self.site.site_static_url('_static','_jslib', cpfile)
        rebuild = True
        if os.path.isfile(cppath):
            rebuild = False
        if rebuild:
            path = self.site.site_static_path('_static','_jslib')
            if not os.path.exists(path):
                os.makedirs(path)
            call_params = ['java','-jar',os.path.join(os.path.dirname(__file__),'compiler.jar')]
            for path in jsfiles:
                call_params.append('--js=%s'%path)
            call_params.append('--js_output_file=%s'%cppath)
            call(call_params)
        return jspath
        
    def _jscompress(self, jsfiles):
        ts = str(max([os.path.getmtime(fname) for fname in jsfiles]))
        key = '-'.join(jsfiles)
        cpfile = '%s.js' % hashlib.md5(key+ts).hexdigest()
        cppath = self.site.site_static_path('_static','_jslib', cpfile)
        jspath = self.site.site_static_url('_static','_jslib', cpfile)
        rebuild = True
        if os.path.isfile(cppath):
            cpf = file(cppath, 'r')
            tsf = cpf.readline()
            cpf.close()
            if ts in tsf:
                rebuild = False
        if rebuild:
            path = self.site.site_static_path('_static','_jslib')
            if not os.path.exists(path):
                os.makedirs(path)
            cpf = file(cppath, 'w')
            cpf.write('// %s\n' % ts)
            for fname in jsfiles:
                f = file(fname)
                js = f.read()
                f.close()
                cpf.write(jsmin(js))
                cpf.write('\n\n\n\n')
            cpf.close()
        return jspath
    
    def get_css_requires(self, requires=None):
        requires = list(set([r for r in (requires or self.css_requires) if r]))
        requires.reverse()
        filepath = os.path.splitext(self.filepath)[0]
        css_requires = []
        css_media_requires = {}
        for css in requires:
            if css:
                if ':' in css:
                    css, media = css.split(':')
                else:
                    media = None
                csslist = self.getResourceList(css,'css')
                if csslist:
                    csslist.reverse()
                    css_uri_list = [self.getResourceUri(css) for css in csslist]
                    if media:
                        css_media_requires.setdefault(media,[]).extend(css_uri_list)
                    else:
                        css_requires.extend(css_uri_list)
        if os.path.isfile('%s.css' % filepath):
            css_requires.append(self.getResourceUri('%s.css' % filepath))
        if os.path.isfile(self.resolvePath('%s.css' % self.pagename)):
            css_requires.append('%s.css' % self.pagename)
        return css_requires, css_media_requires
        
    def getResourceUri(self, path, ext=None):
        fpath=self.getResource(path, ext=ext)
        if not fpath:
            return
        if fpath.startswith(self.site.site_path):
            uripath=fpath[len(self.site.site_path):].lstrip('/').split(os.path.sep)
            return self.site.site_static_url(*uripath)
        elif fpath.startswith(self.site.pages_dir):
            uripath=fpath[len(self.site.pages_dir):].lstrip('/').split(os.path.sep)
            return self.site.pages_static_url(*uripath)
        elif fpath.startswith(self.package_folder):
            uripath=fpath[len(self.package_folder):].lstrip('/').split(os.path.sep)
            return self.site.pkg_static_url(self.packageId,*uripath)
        else:
            for rsrc,rsrc_path in self.site.resources.items():
                if fpath.startswith(rsrc_path):
                    uripath=fpath[len(rsrc_path):].lstrip('/').split(os.path.sep)
                    return self.site.rsrc_static_url(rsrc,*uripath)
        
    def getResource(self, path, ext=None):
        result=self.getResourceList(path=path,ext=ext)
        if result:
            return result[0]

    def getResourceList(self, path, ext=None):
        """Find a resource in current _resources folder or in parent folders one"""
        result=[]
        if ext and not path.endswith('.%s' % ext): path = '%s.%s' % (path, ext)
        for dpath in self.resourceDirs:
            fpath = os.path.join(dpath, path)
            if os.path.exists(fpath):
                result.append(fpath)
        return result 

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
                root=page.borderContainer(design='sidebar', height='100%', nodeId='_gnrRoot',_class='hideSplitter', 
                                            regions='^_clientCtx.mainBC')
                self.debugger.right_pane(root)
                self.debugger.bottom_pane(root)
                self.mainLeftContent(root,region='left',splitter=True, nodeId='gnr_main_left')
                rootwdg = self.rootWidget(root, region='center', nodeId='_pageRoot')
                self.main(rootwdg, **kwargs)
                self.onMainCalls()
                self._createContext(root)
                if self.user:
                    self.site.pageLog(self,'open')

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
        request_kwargs['mako']=self.mako_template()
    
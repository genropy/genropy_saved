# -*- coding: UTF-8 -*-
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
core.py

Created by Giovanni Porcari on 2007-03-24.
Copyright (c) 2007 Softwell. All rights reserved.
"""
import hashlib
import os
import sys
import time
import datetime
import traceback
import random
import itertools
import urllib
import zipfile
import StringIO


#from decimal import Decimal

from gnr.core.gnrlog import gnrlogging
from gnr.core.gnrlang import optArgs, timer_call

gnrlogger = gnrlogging.getLogger('gnr.web.gnrwebcore')


#from mako.template import Template
try:
    import json
except:
    import simplejson as json

from mako.lookup import TemplateLookup

from gnr.core.gnrbag import Bag, DirectoryResolver, TraceBackResolver

from gnr.core.gnrlang import GnrObject

from gnr.core.gnrlang import getUuid, NotImplementedException
from gnr.core.gnrstring import splitAndStrip, toText, toJson
from gnr.core import gnrdate

from gnr.web.jsmin import jsmin

from gnr.web.gnrwebstruct import  GnrDomSrc_dojo_11, GnrDomSrc_dojo_12,GnrDomSrc_dojo_13, GnrGridStruct

#from gnr.web.gnrwebreqresp import GnrWebRequest, GnrWebResponse
#from gnr.web.gnrwebapphandler import GnrProcessHandler
from gnr.sql.gnrsql_exceptions import GnrSqlSaveChangesException

CONNECTION_TIMEOUT = 3600
CONNECTION_REFRESH = 20
AUTH_OK=0
AUTH_NOT_LOGGED=1
AUTH_FORBIDDEN=-1


class GnrWebClientError(Exception):
    pass

class GnrWebServerError(Exception):
    pass


class GnrBaseWebPage(GnrObject):
    
    def __init__(self, request, customclass, filepath, home_uri, response=None, **kwargs):
        raise NotImplementedException()
    
    def newCookie(self, name, value, **kw):
        return self.request.newCookie(name, value, **kw)
        
    def newMarshalCookie(self, name, value, secret=None, **kw):
        return self.request.newMarshalCookie(name,value,secret=secret,**kw)

    def raiseUnauthorized(self):
        raise NotImplementedException()
    
    def add_response_header(self,header,value):
        raise NotImplementedException()
    
    def get_request_header(self,header):
        raise NotImplementedException()
        
    def get_cookie(self, cookieName, cookieType, secret = None,  path=None):
        return self.request.get_cookie(cookieName, cookieType,
                                    secret = secret,  path =path)

    def add_cookie(self,cookie):
        self.response.add_cookie(cookie)

    def get_session(self, **kwargs):
        return self._request.environ['beaker.session']
        
    def _get_clientContext(self):
        cookie=self.get_cookie('genroContext','simple')
        if cookie:
            return Bag(urllib.unquote(cookie.value))
        else:
            return Bag()
    
    def _set_clientContext(self,bag):
        value=urllib.quote(bag.toXml())
        cookie=self.get_cookie('genroContext','simple', path=self.siteUri)
        cookie.value = value
        self.add_cookie(cookie)
        
    clientContext = property(_get_clientContext,_set_clientContext)
        
    def _get_filename(self):
        try:
            return self._filename
        except AttributeError:
            self._filename = os.path.basename(self.filepath)
            return self._filename
    filename = property(_get_filename)
       
    def get_site_id(self):
        raise NotImplementedException()
    
    def _get_siteFolder(self):
        raise NotImplementedException()
    _siteFolder = property(_get_siteFolder)
    
    def _get_folders(self):
        raise NotImplementedException()
    #folders = property(_get_folders)
    
    def _get_sitepath(self):
        raise NotImplementedException()
    sitepath = property(_get_sitepath)
    
    def _get_canonical_filename(self):
        return self.filename
    canonical_filename = property(_get_canonical_filename)
    
    def __siteFolder(self, *args,  **kwargs):
        raise NotImplementedException()
    
    def _get_siteUri(self):
        return self._home_uri
    siteUri = property(_get_siteUri)
    
    def _get_parentdirpath(self):
        raise NotImplementedException()
    parentdirpath = property(_get_parentdirpath)
    
    def _initialize(self, customclass, filepath, home_uri=None, page_id=None, sitepath=None,
                 _rpc_resultPath=None,xxcnt=None, _user_login=None, **kwargs):
        self._rpc_resultPath=_rpc_resultPath
        self.response.add_header('Pragma','no-cache')
        self.page_id = page_id or getUuid()
        self.filepath = filepath # TOGLIERE ????
        self._user_login = _user_login
        self.kwargs = kwargs
        self._htmlHeaders=[]
        self._cliCtxData = Bag()
        if home_uri:
            self._home_uri=home_uri
        if sitepath:
            self._sitepath=sitepath
        else:
            self._sitepath=os.path.dirname(os.path.dirname(self.filepath))
        self.folders= self._get_folders()
        self.pagename = os.path.splitext(os.path.basename(self.filename))[0]
        self.pagepath = self.filename.replace(self.folders['pages'], '')
        self.theme = getattr(customclass, 'theme', None) or self.config['dojo?theme'] or 'tundra'
        self.dojoversion = getattr(customclass, 'dojoversion', None) or self.config['dojo?version'] or '11'
        self.pagetemplate = getattr(customclass, 'pagetemplate', None) or self.config['dojo?pagetemplate']
        self.maintable = getattr(customclass, 'maintable', None)
        self.js_requires = splitAndStrip( getattr(customclass, 'js_requires', ''),',')
        self.css_requires = splitAndStrip(getattr(customclass, 'css_requires', ''),',')
        py_requires = splitAndStrip(getattr(customclass, 'py_requires', '') ,',')
        self.eagers = getattr(customclass, 'eagers', {})
        self._baseMixins()
        self._pyrequiresMixin(py_requires)
        self.mixin(customclass)
        self._customPageMixins()
        self.css_requires.reverse()
        if kwargs.has_key('debug'): 
            self.debug_mode = True
            del kwargs['debug']
        else:
            self.debug_mode = False
        self._dbconnection=None
    
    def importPageModule(self, page_path, pkg=None):
         if not pkg:
             pkg = self.packageId
         return gnrImport(self.site.pkg_static_path(pkg,(page_path.split('/'))))
        
    def mixinFromPage(self,kls,pkg=None):
        if isinstance(kls,basestring):
            page_path, kls_name = kls.split(':')
            module = importPageModule(page_path,pkg=pkg)
            kls = getattr(module, kls_name)
        self.mixin(kls)
    
    def getUuid(self):
        return getUuid()
        
    def _baseMixins(self):
        pkgId = self.packageId
        pkg=None
        if pkgId:
            pkg = self.application.packages[pkgId]
        if pkg:
            self.mixin(pkg.webPageMixin) # first the package standard
        self.mixin(self.application.webPageCustom) # then the application custom
        if pkg:
            self.mixin(pkg.webPageMixinCustom) # finally the package custom

    def _customPageMixins(self):
        """Look in the instance custom folder for a file named as the current webpage"""
        if self.packageId:
            filepath = self.filepath.split(os.path.sep)
            if len(filepath) > 1: #the page is into a package, not root level
                filepath = list(filepath[1:])
                filepath[-1] = filepath[-1].replace('.pyc','.py')
                customPagePath=os.path.join(self.application.customFolder, self.packageId, 'webpages', *filepath)
                if os.path.isfile(customPagePath):
                    self.mixin('%s:%s' % (customPagePath,'WebPage'))
                
    def _pyrequiresMixin(self, py_requires):
        for mix in py_requires:
            if mix:
                modName, clsName = mix.split(':')
                modPathList = self.getResourceList(modName, 'py') or []
                if modPathList:
                    modPathList.reverse()
                    for modPath in modPathList:
                        self.mixin('%s:%s' % (modPath, clsName))
                else:
                    raise GnrWebServerError('Cannot import component %s' % modName)

        
    def _index(self ,**kwargs):
        self.kwargs.update(kwargs)
        self.onInit()
        if self._user_login:
            user=self.user # if we have an embedded login we get the user right now
        
        try:
            if 'mako' in self.kwargs:
                result = self.makoTemplate(path=self.kwargs['mako'], **self.kwargs)
            elif 'rml' in self.kwargs:
                result = self.rmlTemplate(path=self.kwargs['rml'], **self.kwargs)
            elif 'method' in self.kwargs:
                result = self._rpcDispatcher(**self.kwargs)
            else:
                result = self.indexPage()
                self.session.loadSessionData()
                self.session.pagedata['pageArgs'] = self.kwargs
                self.session.pagedata['page_id'] = self.page_id
                self.session.pagedata['connection_id'] = self.connection.connection_id
                self.session.pagedata['pagepath'] = self.pagepath
                self.session.saveSessionData()
        except:
            self._onEnd()
            raise 
        self._onEnd()
        return result
        
    def addHtmlHeader(self,tag,innerHtml='',**kwargs):
        attrString=' '.join(['%s="%s"' % (k,str(v)) for k,v in kwargs.items()])
        self._htmlHeaders.append('<%s %s>%s</%s>'%(tag,attrString,innerHtml,tag))
        
    
    def _css_dojo_d11(self,theme=None):
        theme=theme or self.theme
        return ['dojo/resources/dojo.css',
                'dijit/themes/dijit.css',
                'dijit/themes/%s/%s.css' % (theme,theme),
                'dojox/grid/_grid/Grid.css',
                'dojox/grid/_grid/%sGrid.css' % theme
                ]
    
    def _gnrjs_d11(self):
        return ['gnrbag','genro', 'genro_widgets', 'genro_rpc', 'genro_patch',
                                           'genro_dev','genro_dlg','genro_frm','genro_dom','gnrdomsource',
                                           'genro_wdg','genro_src','gnrlang','gnrstores'
                                           #,'soundmanager/soundmanager2'
                                           ]
    
    def _css_genro_d11(self):
           return {'all': ['gnrbase'], 'print':['gnrprint']}
           
    def _css_dojo_d14(self,theme=None):
        theme=theme or self.theme
        return ['dojo/resources/dojo.css',
                'dijit/themes/dijit.css',
                'dijit/themes/%s/%s.css' % (theme,theme),
                'dojox/grid/_grid/Grid.css',
                'dojox/grid/_grid/%sGrid.css' % theme
                ]
    
    def _gnrjs_d14(self):
        return ['gnrbag','genro', 'genro_widgets', 'genro_rpc', 'genro_patch',
                                           'genro_dev','genro_dlg','genro_frm','genro_dom','gnrdomsource',
                                           'genro_wdg','genro_src','gnrlang','gnrstores'] 
    def _css_genro_d14(self):
           return {'all': ['gnrbase'], 'print':['gnrprint']}

    def get_css_genro(self, gnrlibpath):
        css_genro = getattr(self, '_css_genro_d%s' % self.dojoversion)()
        for media in css_genro.keys():
            css_genro[media] = [self.resolvePathAsUrl('gnrjs',gnrlibpath,'css', '%s.css' % f, folder='*lib') for f in css_genro[media]]
        return css_genro
        
    def get_css_requires(self):
        filename = os.path.splitext(os.path.basename(self.filename))[0]
        css_requires=[]
        for css in self.css_requires:
            if css:
                csslist = self.getResourceList(css,'css')
                if csslist:
                    csslist.reverse()
                    css_requires.extend( [self.diskPathToUri(css) for css in csslist])
        if os.path.isfile(self.resolvePath('%s.css' % filename)):
            css_requires.append(self.diskPathToUri(self.resolvePath('%s.css' % filename)))
        return css_requires

    def get_bodyclasses(self):
        return '%s _common_d11 pkg_%s page_%s' % (self.theme, self.packageId, self.pagename)
    
    def getPublicMethod(self, prefix, method):
        if '.' in method:
            proxy_name, submethod = method.split('.',1)
            proxy_object = getattr(self, proxy_name, None)
            if not proxy_object:
                proxy_class = getattr(self.__module__,proxy_name.capitalize(), None)
                if proxy_class:
                    proxy_object = proxy_class(self)
                    setattr(self, proxy_name, proxy_object)
            if proxy_object:
                handler = getattr(proxy_object, '%s_%s' % (prefix,submethod), None)
        else:
            handler = getattr(self, '%s_%s' % (prefix,method))
        return handler
                
    def htmlHeaders(self):
        pass
        
    def indexPage(self):
        startArgs = dict(self.kwargs)
        charset='utf-8' # c'era una virgola, quindi diventava una tupla, voluto o errore?
        
        filename = os.path.splitext(os.path.basename(self.filename))[0]
        dirname=os.path.dirname(self.filename)
        if not self.pagetemplate:
           tpl = 'standard.tpl'
        else:
           if isinstance(self.pagetemplate, basestring):
               tpl = self.pagetemplate
           else:
               tpl = '%s.%s' % (self.pagename, 'tpl')    
        tpldirectories=[self.parentdirpath]+self.resourceDirs+[self.resolvePath('gnrjs','gnr_d%s' % self.dojoversion,'tpl',folder='*lib')]
        lookup=TemplateLookup(directories=tpldirectories, output_encoding='utf-8', encoding_errors='replace')
        try:
            mytemplate = lookup.get_template(tpl)
        except:
            raise str("No template %s found in %s" % (tpl, str(tpldirectories)))
        debug = startArgs.get('jsdebug')
        arg_dict = {}
        self.htmlHeaders()
        arg_dict['customHeaders']=self._htmlHeaders
        arg_dict['charset'] = charset
        arg_dict['filename'] = self.pagename
        arg_dict['startArgs'] = toJson(startArgs)
        arg_dict['page_id'] = self.page_id or getUuid()
        arg_dict['bodyclasses'] = self.get_bodyclasses()
        dojolib=self.resolvePathAsUrl('dojo/dojo_%s/dojo/dojo.js'%self.dojoversion, folder='*lib')
        arg_dict['dojolib'] = dojolib
        arg_dict['djConfig'] = "parseOnLoad: false, isDebug: %s, locale: '%s'" % (self.isDeveloper() and 'true' or 'false',self.locale)
        arg_dict['gnrModulePath'] = '../../gnrjs'
        gnrimports = getattr(self, '_gnrjs_d%s' % self.dojoversion)()
        gnrlibpath='gnr_d%s' % self.dojoversion
        if debug or self.isDeveloper():
            arg_dict['genroJsImport'] = [self.resolvePathAsUrl('gnrjs', gnrlibpath,'js', '%s.js' % f, folder='*lib') for f in gnrimports]
        else:
            jsfiles = [self.resolvePath('gnrjs', gnrlibpath,'js', '%s.js' % f, folder='*lib') for f in gnrimports]
            js=self.resolvePathAsUrl(self._jscompress(jsfiles))
            arg_dict['genroJsImport'] = [self.resolvePathAsUrl(self._jscompress(jsfiles),folder='*pages')]
            
        
        css_dojo = getattr(self, '_css_dojo_d%s' % self.dojoversion)()
        arg_dict['css_dojo'] = [self.resolvePathAsUrl('dojo/dojo_%s/%s' % (self.dojoversion,f), folder='*lib') for f in css_dojo]

        arg_dict['css_genro'] = self.get_css_genro(gnrlibpath)

        js_requires = [x for x in [self.getResourceUri(r,'js') for r in self.js_requires ] if x]
        if os.path.isfile(self.resolvePath('%s.js' % self.pagename)):
            js_requires.append('%s.js' % self.pagename)
        arg_dict['js_requires'] = js_requires
        css_requires = self.get_css_requires()
        if os.path.isfile(self.resolvePath('%s.css' % self.pagename)):
            css_requires.append('%s.css' % self.pagename)
        arg_dict['css_requires'] = css_requires
        return mytemplate.render(mainpage=self, **arg_dict)
    
    def _jscompress(self, jsfiles):
        ts = str(max([os.path.getmtime(fname) for fname in jsfiles]))
        key = '-'.join(jsfiles)
        cpfile = '%s.js' % hashlib.md5(key+ts).hexdigest()
        
        cppath = self.resolvePath('_jslib', cpfile, folder='*pages')
        jspath = '_jslib/%s'%cpfile
        rebuild = True
        if os.path.isfile(cppath):
            cpf = file(cppath, 'r')
            tsf = cpf.readline()
            cpf.close()
            if ts in tsf:
                rebuild = False
        if rebuild:
            path=os.path.join(self.siteFolder, 'pages', '_jslib')
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
    
    def rpc_jscompress(self, js, **kwargs):
        cppath = self.resolvePath('temp','js', js, folder='*data')
        f = file(cppath)
        js = f.read()
        f.close()
        return js
    
    def rpc_decodeDatePeriod(self, datestr, workdate=None, locale=None):
        workdate = workdate or self.workdate
        locale = locale or self.locale
        period=datestr
        valid=False
        try:
            returnDate = gnrdate.decodeDatePeriod(datestr, workdate=workdate, locale=locale, returnDate=True)
            valid=True
        except:
            returnDate = (None, None)
            period=None
        result = Bag()
        result['from'] = returnDate[0]
        result['to'] = returnDate[1]
        result['prev_from'] = gnrdate.dateLastYear(returnDate[0])
        result['prev_to'] = gnrdate.dateLastYear(returnDate[1])
        result['period'] = period
        result['valid']=valid
        result['period_string'] = gnrdate.periodCaption(*returnDate,locale=locale)
        return result
    
    def rpc_ping(self, **kwargs):
        pass
    
    def rpc_setInServer(self, path, value=None, **kwargs):
        self.session.modifyPageData(path, value)
    
    def rpc_setViewColumns(self, contextTable=None, gridId=None, relation_path=None, contextName=None, query_columns=None, **kwargs):
        self.app.setContextJoinColumns(table=contextTable, contextName=contextName, reason=gridId,
                                       path=relation_path, columns=query_columns)
    
    def onEnd(self):
        pass
    
    def _onEnd(self):
        self.handleMessages()
        if hasattr(self, '_localizer'):
            self.session.loadSessionData()
            localization={}
            localization.update(self.session.pagedata['localization'] or {})
            localization.update(self.localizer)
            self.session.setInPageData('localization', localization)
            self.session.saveSessionData()
        if hasattr(self, '_connection'):
            if self.user:
                self.connection._finalize()
        if hasattr(self, '_app'):
            self._app._finalize(self)
        self.onEnd()
    
    def mixins(self):
        """Implement this method in your page for mixin the page with methods from the local _resources folder
        @return: list of mixin names, moduleName:className"""
        return []
    
    def onInit(self):
        # subclass hook
        pass
        
    def requestWrite(self, txt, encoding='utf-8'):
        self.responseWrite(txt,encoding=encoding)

    def responseWrite(self, txt, encoding='utf-8'):
        self.response.write(txt.encode(encoding))

    def log(self, msg):
        if getattr(self, 'debug', False):
            f = file(self.logfile, 'a')
            f.write('%s -- %s\n' % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), msg))
            f.close()
            
    def _get_localizer(self): 
        if not hasattr(self, '_localizer'):
            self._localizer={}
            self.missingLoc=False
        return self._localizer
    localizer = property(_get_localizer) 
    
    def isLocalizer(self) :
        return ((self.userTags and ('_TRD_' in self.userTags)) or self.pageArgs.get('_loc_'))
        
    def isDeveloper(self) :
        return ((self.userTags and ('_DEV_' in self.userTags)) or self.pageArgs.get('_dev_'))
        
    def _get_siteStatus(self):
        if not hasattr(self, '_siteStatus'):
            path = os.path.join(self.siteFolder, 'data', '_siteStatus.xml')
            
            if os.path.isfile(path):
                self._siteStatus=Bag(path)
            else:
                self._siteStatus=Bag()
        return self._siteStatus
    siteStatus = property(_get_siteStatus)
    
    def siteStatusSave(self):
        if hasattr(self, '_siteStatus'):
            path = os.path.join(self.siteFolder, 'data', '_siteStatus.xml')
            self._siteStatus.toXml(path)
            
    def _get_user(self):
        """Get the user from hidden _user attribute."""
        if not self._user:
            self._user = self.connection.appSlot.get('user')
        return self._user
        
    user = property(_get_user)
        
    def _get_userTags(self):
        return self.connection.appSlot.get('tags')
    userTags = property(_get_userTags)
    
    def _get_avatar(self):
        if not hasattr(self, '_avatar'):
            self._avatar = self.application.getAvatar(self.user)
        return self._avatar
    avatar = property(_get_avatar)
    
    def updateAvatar(self):
        """Reload the avatar, recalculate tags, and save in cookie"""
        self.connection.updateAvatar(self.avatar)
        
    def pageAuthTags(self, method=None, **kwargs):
        return ""
        
    def checkPermission(self, pagepath, relative=True):
        if relative:
            pagepath = self.utils.pageFolder(pagepath).replace(self.utils.rootFolder(),'')
        return self.application.checkPagePermission(pagepath, self.userTags)
    
    def rpc_doLogin(self, login=None, guestName=None, **kwargs):
        """Service method that set user's avatar into its connection if
        - The user exists and his password is correct.
        - The user is guest
        """
        loginPars={}
        if guestName:
            avatar = self.application.getAvatar(guestName)
        else:
            avatar = self.application.getAvatar(login['user'], password=login['password'], authenticate=True,page=self)
        if avatar:
            self.connection.updateAvatar(avatar)
            self.site.onAutenticated(avatar)
            login['message'] = ''
            loginPars=avatar.loginPars
        else:
            login['message'] = 'invalid login'
        return (login,loginPars)
    

    def _rpcDispatcher(self, method=None, xxcnt='',**kwargs):
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
        return self.rpc(self, method=method, _auth=auth, **parameters)
        
    def _checkAuth(self, method=None, **parameters):
        auth = AUTH_OK
        pageTags = self.pageAuthTags(method=method, **parameters)
        if pageTags:
            if not self.user:
                auth = AUTH_NOT_LOGGED
            elif not self.application.checkResourcePermission(pageTags, self.userTags):
                auth = AUTH_FORBIDDEN
                
            if auth == AUTH_NOT_LOGGED and method != 'main':# and method!='onClosePage':
                if not self.connection.oldcookie:
                    pass
                    #self.raiseUnauthorized()
                auth = 'EXPIRED'
                
        elif parameters.get('_loginRequired') == 'y':
            auth = AUTH_NOT_LOGGED
        return auth
        
    def pageLocalDocument(self, docname):
        folder = os.path.join(self.connectionFolder, self.page_id)
        if not os.path.isdir(folder):
            os.makedirs(folder)
        return os.path.join(folder, docname)
    
    def freezeSelection(self, selection, name):
        selection.freeze(self.pageLocalDocument(name), autocreate=True)
        
    def unfreezeSelection(self, dbtable, name):
        if isinstance(dbtable, basestring):
            dbtable = self.db.table(dbtable)
        return dbtable.frozenSelection(self.pageLocalDocument(name))

    def _get_connectionFolder(self):
        return self.connection.connectionFolder
    connectionFolder = property(_get_connectionFolder)
    
    def _get_connection(self):
        if not hasattr(self, '_connection'):
            connection = GnrWebConnection(self)
            self._connection = connection
            connection.initConnection()
        return self._connection
    connection = property(_get_connection)
    
    def _get_utils(self):
        if not hasattr(self, '_utils'):
            self._utils = GnrWebUtils(self)
        return self._utils
    utils = property(_get_utils)
    
    def _get_rpc(self):
        if not hasattr(self, '_rpc'):
            self._rpc = GnrWebRpc()
        return self._rpc
    rpc = property(_get_rpc)
    
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
    
#    def _get_html(self):
#        if not hasattr(self, '_html'):
#            self._html = HtmlFormatter()
#        return self._html
#    html = property(_get_html)
    
    def _get_session(self):
        if not hasattr(self, '_session'):
            self._session = GnrWebSession(self, lock=0)
        return self._session
    session = property(_get_session)

    def _get_pageArgs(self):
        return self.session.pagedata['pageArgs'] or {}
    pageArgs = property(_get_pageArgs)
    
    def rpc_updateSessionContext(self, context, path, evt, value=None, attr=None):
        self.session.loadSessionData()
        self.session.setInPageData('context.%s.%s' % (context, path), value, attr)
        self.session.saveSessionData()
        
    def setInClientData(self, _client_path, value, _attributes=None, page_id=None, connection_id=None, fired=False, save=False, **kwargs):
        """@param save: remember to save on the last setInClientData. The first call to setInClientData implicitly lock the session util 
                        setInClientData is called with save=True
        """
        _attributes = dict(_attributes or {})
        _attributes.update(kwargs)
        _attributes['_client_path'] = _client_path
        if connection_id == None or connection_id==self.connection.connection_id:
            self.session.setInPageData('_clientDataChanges.%s' % _client_path.replace('.','_'), 
                                        value, _attributes=_attributes, page_id=page_id)
            if save: self.session.saveSessionData()
        else:
            pass
    
    def sendMessage(self,message):
        self.setInClientData('gnr.servermsg', message, fired=True, save=True,
                            src_page_id=self.page_id,src_user=self.user,src_connection_id=self.connection.connection_id)
            
    def clientDataChanges(self):
        if self.session.pagedata['_clientDataChanges']:
            self.session.loadSessionData()
            result = self.session.pagedata.pop('_clientDataChanges') or Bag()
            self.session.saveSessionData()
            return result
        

    def _get_catalog(self):
        if not hasattr(self, '_catalog'):
            self._catalog = self.application.catalog
        return self._catalog
    catalog = property(_get_catalog)
    
    def _set_locale(self, val):
        self._locale = val
    def _get_locale(self): # TODO IMPLEMENT DEFAULT FROM APP OR AVATAR 
        if not hasattr(self, '_locale'):
            self._locale = self.connection.locale or self.request.headers.get('Accept-Language', 'en').split(',')[0] or 'en'
        return self._locale
    locale = property(_get_locale, _set_locale)
    
    def rpc_changeLocale(self, locale):
        self.connection.locale = locale.lower()
        
    def translateText(self, txt):
        key='%s|%s' % (self.packageId, txt.lower())
        localelang = self.locale.split('-')[0]
        loc = self.application.localization.get(key)
        missingLoc=True
        if not loc:
            key=txt
            loc = self.application.localization.get(txt)
        if loc:
            loctxt = loc.get(localelang) 
            if loctxt :
                missingLoc=False
                txt=loctxt
        else:
            self._translateMissing(txt)
            self.application.localization[key] = {}
        if self.isLocalizer():
            self.localizer[key]=self.application.localization[key]
            self.missingLoc=self.missingLoc or missingLoc
        return txt
        
    def _(self, txt):
        if txt.startswith('!!'):
            txt = self.translateText(txt[2:])
        return txt
    
    def _translateMissing(self, txt):
        if not self.packageId: return
        missingpath = os.path.join(self.siteFolder, 'data', '_missingloc', self.packageId)
        if isinstance(txt, unicode): 
            txtmd5 = txt.encode('utf8', 'ignore')
        else:
            txtmd5 = txt
        fname = os.path.join(missingpath, '%s.xml' % hashlib.md5(txtmd5).hexdigest())
        
        if not os.path.isfile(fname):
            b = Bag()
            b['txt'] = txt
            b['pkg'] = self.packageId
            old_umask = os.umask(2)
            b.toXml(fname, autocreate=True)
            os.umask(old_umask)
        
    def toText(self, obj, locale=None, format=None, mask=None, encoding=None, dtype=None):
        locale = locale or self.locale
        return toText(obj, locale=locale, format=format, mask=mask, encoding=encoding)

    def _get_config(self):
        if not hasattr(self, '_config'):
            self._config = Bag(self.utils.absoluteDiskPath('siteconfig.xml'))
        return self._config
    config = property(_get_config)
    
    def getDomainUrl(self, path, **kwargs):
        params = urllib.urlencode(kwargs)
        path = os.path.join(self.folders['pages'].replace(self.folders['document_root'], ''), path)
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
        
    def getAbsoluteUrl(self, path, **kwargs):
        """return an external link to the page
        @param path: the path to the page from 'pages' folder
        """
        return self.request.construct_url(self.getDomainUrl(path, **kwargs))

    def resolvePathAsUrl(self, *args,  **kwargs):
        return self.diskPathToUri(self.resolvePath(*args, **kwargs))
        
    def resolvePath(self, *args, **kwargs):
        folder = kwargs.pop('folder', None)
        sitefolder = self.siteFolder
        if folder == '*data':
            diskpath = os.path.join(sitefolder, 'pages','..', 'data',  *args)
            return diskpath
        elif folder == '*users':
            diskpath = os.path.join(sitefolder,'pages','..', 'data', '_users', *args)
            return diskpath
        elif folder == '*home':
            diskpath = os.path.join(sitefolder,'pages','..', 'data', '_users', self.user, *args)
            return diskpath
        elif folder == '*pages':
            diskpath = os.path.join(sitefolder, 'pages',  *args)
        elif folder == '*lib':
            diskpath = os.path.join(sitefolder, 'pages', '_lib', *args)
        elif folder == '*static':
            diskpath = os.path.join(sitefolder, 'pages', 'static', *args)
        elif folder == '*common':
            diskpath = os.path.join(sitefolder, 'pages', '_common_d11' , *args)
        else:
            diskpath = os.path.join(os.path.dirname(self.filename), *args)
        diskpath = os.path.normpath(diskpath)
        return diskpath
        
    def diskPathToUri(self, tofile, fromfile=None):
        fromfile = fromfile or self.filename
        pagesfolder = self.folders['pages']
        relUrl = tofile.replace(pagesfolder, '').lstrip('/')
        path = fromfile.replace(pagesfolder, '')
        rp = '../'*(len(path.split('/'))-1)
        
        path_info = self.request.path_info
        if path_info: # != '/index'
            rp = rp + '../'*(len(path_info.split('/'))-1)
        return '%s%s' % (rp, relUrl)
    
    def _get_siteName(self):
        return os.path.basename(self.siteFolder.rstrip('/'))
    siteName = property(_get_siteName)
    
    def _get_app(self):
        raise NotImplementedException()
    app = property(_get_app) #cambiare in appHandler e diminuirne l'utilizzo al minimo
    
    def _get_db(self):
        return self.app.db
    db = property(_get_db)
    
    def _get_dbconnection(self):
        if not self._dbconnection: 
            self._dbconnection=self.db.adapter.connect()
        return 
    dbconnection = property(_get_dbconnection)
    
    
    def _get_application(self):
        if not hasattr(self,'_application'):
            self._application= self.app.gnrapp
        return self._application
    application = property(_get_application)
    
    def _get_packages(self):
        return self.db.packages
    packages = property(_get_packages)
    
    def _get_package(self):
        pkgId = self.packageId
        if pkgId:
            return self.db.package(pkgId)
    package = property(_get_package)


    
    def _get_tblobj(self):
        if self.maintable:
            return self.db.table(self.maintable)
    tblobj = property(_get_tblobj)
    
    def _get_workdate(self):
        if not hasattr(self,'_workdate'):
            workdate = self.pageArgs.get('_workdate_')
            if not workdate or not self.userTags or not('superadmin' in self.userTags):
                workdate =  self.session.pagedata['workdate'] or datetime.date.today()
            if isinstance(workdate, basestring):
                workdate = self.application.catalog.fromText(workdate, 'D')
            self._workdate = workdate
        return self._workdate
    
    def _set_workdate(self, workdate):
        self.session.setInPageData('workdate', workdate)
        self.session.saveSessionData()
        self._workdate = workdate

    workdate = property(_get_workdate, _set_workdate)
    
    def _get_logfile(self):
        if not hasattr(self, '_logfile'):
            logdir = os.path.normpath(os.path.join(self.utils.directory, '..', 'data', 'logs'))
            if not os.path.isdir(logdir):
                os.makedirs(logdir)
            self._logfile = os.path.join(logdir, 'error_%s.log' % datetime.date.today().strftime('%Y%m%d'))
        return self._logfile
    logfile = property(_get_logfile)
    
    #def _get_siteHandler(self):
    #    if not hasattr(self, '_siteHandler'):
    #        global GNR_PROCESS_HANDLER
    #        try: 
    #            GNR_PROCESS_HANDLER # fare come thread.local
    #        except NameError :
    #            self.newprocess = True
    #            GNR_PROCESS_HANDLER = GnrProcessHandler()
    #        self._siteHandler = GNR_PROCESS_HANDLER.getSiteHandler(self)
    #    return self._siteHandler
    #siteHandler = property(_get_siteHandler)
    
    
    def _findInheritedResource(self, moduleName,ext='py',uri=False):
        """Find a resource in current _resources folder or in parent folders one"""
        if not moduleName.endswith('.%s'%ext):
            moduleName = '%s.%s' % (moduleName,ext)
        pagesPath = os.path.dirname(self.sitepath)
        curdir = os.path.dirname(self.filename)
        while curdir.startswith(pagesPath):
            fpath = os.path.join(curdir, '_resources', moduleName)
            if os.path.isfile(fpath):
                if uri:
                    fpath=self.utils.diskPathToUri(fpath)
                return fpath
            curdir = os.path.dirname(curdir)
            
    def rpc_menu_browse(self, path=None):
        try:
            cacheTime = self.application.getResource('menues.%s?cacheTime' % 'browse', pkg=self.packageId) or 60
        except:
            cacheTime = 60
        
        menu=self.newSourceRoot()
        dirRoot = self.application.webpageIndex['root']
        if not path:
            if self.folders['current'] == self.folders['pages']:
                self._addMenulines(menu,dirRoot,cacheTime, path)
            else:
                dirFolder = dirRoot[path]
                self._addMenulines(menu, dirFolder, cacheTime, path)
                menu.menuline('-')
                self._addMenulines(menu.menuline('Root').menu(),dirRoot,cacheTime, path)
        else:
            dirFolder = dirRoot[path]
            self._addMenulines(menu,dirFolder,cacheTime, path)
        return menu

    def _addMenulines(self, menu, dirbag, cacheTime, path):
        for n in dirbag.nodes:
            k=n.label
            href=self.utils.diskPathToUri(n.getAttr('abs_path'))
            resolver=n.resolver    
            if not resolver is None:
                indexnode = n.getValue().getNode('index_py')
                if indexnode and self.application.checkResourcePermission(indexnode.getAttr('pageAuthTags'), self.userTags):
                    label = indexnode.getAttr('info', {}).get('label', k.replace('_',' ').capitalize())
                    if path:
                        newpath = '%s.%s' % (path, k)
                    else:
                        newpath = k
                    menu.menuline(label).menu().remote('menu_browse',cacheTime=cacheTime, path=newpath)
            elif not k.lower().startswith('index'):
                if self.application.checkResourcePermission(n.getAttr('pageAuthTags'), self.userTags):
                    if k.endswith('_py'):
                        k=k[0:-3]
                    label = n.getAttr('info', {}).get('label', k.replace('_',' ').capitalize())
                    menu.menuline(label, href=href)
                    
    def formSaver(self,formId,table=None,method=None,_fired='',datapath=None,
                    resultPath='dummy',changesOnly=True,onSaved=None,saveAlways=False,**kwargs):
        method = method or 'saveRecordCluster'
        controller = self.pageController()
        data = '==genro.getFormCluster("%s");' 
        onSaved = onSaved or ''
        if changesOnly:
            data = '==genro.getFormChanges("%s");'
        controller.dataController('genro.formById("%s").save(always)' %formId,_fired=_fired,
                                 datapath=datapath,always=saveAlways)
        kwargs['fireModifiers'] = _fired.replace('^','=')
        controller.dataRpc(resultPath, method=method ,nodeId='%s_saver' %formId ,_POST=True,
                           datapath=datapath,data=data %formId, 
                           _onResult='genro.formById("%s").saved();%s;' %(formId,onSaved), 
                           table=table,**kwargs)
                       
    def formLoader(self,formId,resultPath,table=None,pkey=None,  datapath=None,
                    _fired=None,loadOnStart = False,lock=False,
                    method=None,onLoading=None,onLoaded=None,loadingParameters=None,
                    **kwargs):
        pkey = pkey or '*newrecord*'
        method = method or 'loadRecordCluster'
        onResultScripts=[]
        onResultScripts.append('genro.formById("%s").loaded()' % formId)
        if onLoaded:
            onResultScripts.append(onLoaded)
        loadingParameters = loadingParameters or '=gnr.tables.maintable.loadingParameters'
        controller = self.pageController()
        controller.dataController('genro.formById("%s").load();' %formId,
                                _fired=_fired, _onStart=loadOnStart,_delay=1,datapath=datapath)
                    
        controller.dataRpc(resultPath, method=method, pkey=pkey, table=table,
                           nodeId='%s_loader' %formId,datapath=datapath,_onCalling=onLoading,
                           _onResult=';'.join(onResultScripts),lock=lock,
                           loadingParameters=loadingParameters, **kwargs)
                    
    def rpc_loadRecordCluster(self, table=None, pkey=None, recordGetter='app.getRecord', **kwargs):
        table = table or self.maintable
        getterHandler = self.getPublicMethod('rpc', recordGetter)
        record, recinfo = getterHandler(table=table, pkey=pkey, **kwargs)
        return record, recinfo
        

    def rpc_saveRecordCluster(self, data,table=None,_nocommit=False, **kwargs):
        #resultAttr = None #todo define what we put into resultAttr
        resultAttr = {}
        onSavingMethod='onSaving'
        onSavedMethod='onSaved'
        maintable=getattr(self,'maintable') 
        table=table or maintable
        tblobj = self.db.table(table)
        if table!=maintable:
            onSavingMethod='onSaving_%s'% table.replace('.','_')
            onSavedMethod='onSaved_%s' % table.replace('.','_')
        onSavingHandler=getattr(self,onSavingMethod,None)
        onSavedHandler=getattr(self,onSavedMethod,None)
        node = data.getNode('record')
        recordCluster = node.value
        recordClusterAttr = node.getAttr()
        #try:
        if True:
            onSavedKwargs = dict()
            if onSavingHandler:
                onSavedKwargs = onSavingHandler(recordCluster, recordClusterAttr, resultAttr=resultAttr) or {}
            record = tblobj.writeRecordCluster(recordCluster,recordClusterAttr)
            if onSavedHandler:
                onSavedHandler(record, resultAttr=resultAttr,  **onSavedKwargs)
            if not _nocommit:
                self.db.commit()
            return (record[tblobj.pkey],resultAttr)
       # except GnrSqlSaveChangesException, e:
       #     return ('validation_error',{ 'msg':e.message})
       # except Exception, e:
       #     raise e
        
        
    def rpc_deleteRecordCluster(self, data, table=None, **kwargs):
        maintable=getattr(self,'maintable') 
        table=table or maintable
        tblobj = self.db.table(table)
        node = data.getNode('record')
        recordCluster = node.value
        recordClusterAttr = node.getAttr()
        try: #try:
            self.onDeleting(recordCluster,recordClusterAttr)
            recordClusterAttr['_deleterecord'] = True
            record = tblobj.writeRecordCluster(recordCluster,recordClusterAttr)
            self.onDeleted(record)
            self.db.commit()
            return 'ok'
        except GnrSqlSaveChangesException, e:
            return ('delete_error',{ 'msg':e.message})    
            
    def rpc_deleteRow(self,table,pkey=None,record=None,**kwargs):
        """
            Method for deleting a single record from a given tablename 
            and from a record or its pkey.
        """
        try:
            tblobj = self.db.table(table)
            recordToDelete = record or tblobj.record(pkey,for_update=True, mode='bag')
            if recordToDelete:
                tblobj.delete(recordToDelete)
                self.db.commit()
            else:
                raise 'No record to delete'
        except:
            raise 'deleteRow failed'
                
    def setLoadingParameters(self, table,**kwargs):
        self.pageSource().dataFormula('gnr.tables.%s.loadingParameters' %table.replace('.','_'), 
                                       '',_onStart=True, **kwargs)
                                       
    def onSaving(self, recordCluster, recordClusterAttr, resultAttr=None):
        pass
    
    def onSaved(self, record, resultAttr=None, **kwargs):
        pass
    
    def onDeleting(self, recordCluster, recordClusterAttr):
        pass
    
    def onDeleted(self, record):
        pass
        
    def toJson(self,obj):
        return toJson(obj)
    
    def setOnBeforeUnload(self, root, cb, msg):
        root.script("""genro.checkBeforeUnload = function(e){
                       if (%s){
                           return "%s";
                       }
                }""" % (cb, self._(msg)))
        
        
    def rpc_onClosePage(self, **kwargs):
        self.session.removePageData()
        self.connection.cookieToRefresh()
        self.site.onClosePage()
        
    def mainLeftContent(self,parentBC,**kwargs):
        pass
        
    def onMainCalls(self):
        calls = [m for m in dir(self) if m.startswith('onMain_')]
        for m in calls:
            getattr(self, m)()
        self.onMain()
    
    def pageController(self,**kwargs):
        return self.pageSource().dataController(**kwargs)

    def pageSource(self, nodeid=None):
        if nodeid:
            return self._root.nodeById(nodeid)
        else:
            return self._root
            
    def rootWidget(self, root, **kwargs):
        return root.contentPane(**kwargs)
        
    def main(self, root,**kwargs): #You MUST override this !
        root.h1('You MUST override this main method !!!')
        
    def onMain(self): #You CAN override this !
        pass
    
    def _createContext(self, root):
        if self._cliCtxData:
            self.session.loadSessionData()
            for ctxName, ctxValue in self._cliCtxData.items():
                root.defineContext(ctxName, '_serverCtx.%s' % ctxName, ctxValue, savesession=False)
            self.session.saveSessionData()
                
    def setJoinCondition(self, ctxname, target_fld='*', from_fld='*', condition=None, one_one=None, applymethod=None, **kwargs):
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
        self._cliCtxData['%s.%s_%s' % (ctxname, target_fld.replace('.','_'), from_fld.replace('.','_'))] = Bag(dict(target_fld=target_fld, from_fld=from_fld, condition=condition, one_one=one_one, applymethod=applymethod, params=Bag(kwargs)))
        
    def setJoinColumns(self, ctxname, target_fld, from_fld, joincolumns):
        self._cliCtxData['%s.%s_%s.joincolumns' % (ctxname,
                                                target_fld.replace('.','_'),
                                                from_fld.replace('.','_'))] = joincolumns
    
    
    def forbiddenPage(self, root, **kwargs):
        dlg = root.dialog(toggle="fade", toggleDuration=250, onCreated='widget.show();')
        f = dlg.form()
        f.div(content = 'Forbidden Page',text_align="center",font_size='24pt')
        tbl = f.contentPane(_class='dojoDialogInner').table()
        row = tbl.tr()
        row.td(content='Sorry. You are not allowed to use this page.', align="center",font_size='16pt', color='#c90031')
        cell = tbl.tr().td()
        cell.div(float='right',padding='2px').button('Back', action='genro.pageBack()')
        

    def windowTitle(self):
        return os.path.splitext(os.path.basename(self.filename))[0].replace('_',' ').capitalize()

    def _errorPage(self,err,method=None,kwargs=None):
        page = self.domSrcFactory.makeRoot(self)
        sc=page.stackContainer(height='80ex',width='50em',selected='^_dev.traceback.page')
        p1=sc.contentPane(background_color='silver')
        #msc=sc.menu()
        #msc.menuline('Close traceback',action='genro.wdgById("traceback_main").hide()')
        p1.div('Sorry: an error occurred on server while executing the method:<br> %s <br><br>Check parameters before executing again last command.' % method,
                    text_align='center',padding='1em',font_size='2em',color='gray',margin='auto')
        p1.button(label='See errors',action='FIRE _dev.traceback.page=1',position='absolute',bottom='1em',right='1em')
        accordion = sc.accordionContainer()
        accordion.accordionPane(title='traceback').div(border='1px solid gray',background_color='silver',padding='5px',margin_top='3em').pre(traceback.format_exc())
        errBag = TraceBackResolver()()
        for k, tb in errBag.items():
            currpane = accordion.accordionPane(title=k)
            currpane.div(tb['line'],font_size='1.2em',margin='4px')
            tbl = currpane.table(_class='bagAttributesTable').tbody()
            for node in tb['locals'].nodes:
                v = node.getStaticValue()
                tr = tbl.tr()
                tr.td(node.label, align='right')
                try:
                    if not isinstance(v, basestring):
                        v = str(v)
                    if not isinstance(v, unicode):
                        v = v.decode('ascii','ignore')
                except:
                    v = 'unicode error'
                tr.td(v.encode('ascii','ignore'))
        return page
        
    def userMenu(self,userTags=None,menubag=None,level=None,basepath=None):
        userTags=userTags or self.userTags
        menubag=menubag or self.application.config['menu']
        level=level or 0
        basepath=basepath or []
        result = Bag()
        if not userTags:
            return result
        for node in menubag.nodes:
            allowed=True
            if node.getAttr('tags'):
                allowed=self.application.checkResourcePermission(node.getAttr('tags'), userTags)
            if allowed and node.getAttr('file'):
                allowed = self.checkPermission(node.getAttr('file'))
            if allowed:
                value=node.getStaticValue()
                attributes={}
                attributes.update(node.getAttr())
                currbasepath=basepath
                if 'basepath' in attributes:
                    newbasepath=node.getAttr('basepath')
                    if newbasepath.startswith('/'):
                        currbasepath=[newbasepath]
                    else:
                        currbasepath=basepath+[newbasepath]
                if isinstance(value,Bag):
                    value = self.userMenu(userTags,value,level+1,currbasepath)
                    labelClass = 'menu_level_%i' %level 
                else:
                    value=None
                    labelClass = 'menu_page'
                attributes['labelClass'] = 'menu_shape %s' %labelClass
                filepath=attributes.get('file')
                if filepath and not filepath.startswith('/'):
                    attributes['file'] = os.path.join(*(currbasepath+[filepath]))
                result.setItem(node.label,value,attributes)
        return result
        
    def handleMessages(self):
        messages = self.site.getMessages(user=self.user, page_id=self.page_id, connection_id=self.connection.connection_id) or []
        for message in messages:
            message_body = Bag(message['body'])
            message_type = message['message_type']
            message_id = message['id']
            handler = getattr(self,'msg_%s'%message_type,self.msg_undefined)
            if message['dst_page_id']:
                mode = 'page'
            elif message['dst_connection_id']:
                mode = 'connection'
            elif message['dst_user']:
                mode = 'user'
            getattr(self, 'handleMessages_%s'%mode,lambda *a,**kw: None)(handler=handler, message_id=message_id, message_body=message_body,src_page_id=message['src_page_id'],
                                                                        src_connection_id=message['src_connection_id'],src_user=message['src_user'])
    
    def handleMessages_user(self,handler,**kwargs):
        handler(**kwargs)
        
    def handleMessages_connection(self,handler,**kwargs):
        handler(**kwargs)
            
    def handleMessages_page(self,handler,message_id=None, **kwargs):
        handler(message_id=message_id,**kwargs)
        self.db.rollback()
        self.site.deleteMessage(message_id)
        self.db.commit()
        
    def msg_servermsg(self,message_id=None, message_body=None,src_page_id=None,src_user=None,src_connection_id=None):
        self.setInClientData('gnr.servermsg', message_body['servermsg'], fired=True, save=True,
                            src_page_id=src_page_id,src_user=src_user,src_connection_id=src_connection_id,
                            message_id=message_id)
    
    def msg_servercode(self, message_id=None, message_body=None,src_page_id=None,src_user=None,src_connection_id=None):
        self.setInClientData('gnr.servercode', message_body['servercode'], fired=True, save=True,
                            src_page_id=src_page_id,src_user=src_user,src_connection_id=src_connection_id,
                            message_id=message_id)
    
    def msg_datachange(self, message_id=None, message_body=None,src_page_id=None,src_user=None,src_connection_id=None):
        for change in message_body:
            self.setInClientData(change.attr.pop('_client_data_path'), change.value , _attributes=change.attr, save=True,
                                src_page_id=src_page_id,src_user=src_user,src_connection_id=src_connection_id,
                                message_id=message_id)
    
    
    def msg_undefined(self, message):
        pass
        
    def newSourceRoot(self):
        return self.domSrcFactory.makeRoot(self)
    
    def newGridStruct(self, maintable=None):
        return GnrGridStruct.makeRoot(self, maintable=maintable)
    
    def _get_domSrcFactory(self):
        if self.dojoversion=='11':
            return GnrDomSrc_dojo_11
        elif self.dojoversion=='12':
            return GnrDomSrc_dojo_12
        elif self.dojoversion=='13':
            return GnrDomSrc_dojo_13
    domSrcFactory=property(_get_domSrcFactory)

    def rpc_resolverRecall(self, resolverPars=None, **auxkwargs):
        if isinstance(resolverPars,basestring):
            resolverPars = json.loads(resolverPars) #should never happen
        resolverclass = resolverPars['resolverclass']
        args = resolverPars['args'] or []
        kwargs = {}
        for k,v in (resolverPars['kwargs'] or {}).items():
            k = str(k)
            if k.startswith('_serialized_'):
                pool, k = k.replace('_serialized_','').split('_')
                v = getattr(self, pool)[v]
            kwargs[k] = v
        kwargs.update(auxkwargs)
        self.response.content_type = "text/xml"
        resolverclass=str(resolverclass)
        if resolverclass in globals():
            return globals()[resolverclass](*args,**kwargs)()
        elif hasattr(self, 'class_%s' % resolverclass):
            h=getattr(self, 'class_%s' % resolverclass)
            c=h()
            c(*args,**kwargs)()
        elif hasattr(self, 'globals') and resolverclass in self.globals:
            return self.globals[resolverclass](*args,**kwargs)()
        else:
            #raise str(resolverclass)
            #handle this case!
            pass
    
    def makoTemplate(self,path,striped='odd_row,even_row', **kwargs):
        auth = self._checkAuth()
        if auth != AUTH_OK:
            self.raiseUnauthorized()
            
        if striped:
            kwargs['striped']=itertools.cycle(striped.split(','))
            
        tpldirectories=[os.path.dirname(path), self.parentdirpath]+self.resourceDirs+[self.resolvePath('gnrjs','gnr_d%s' % self.dojoversion,'tpl',folder='*lib')]
        
        lookup=TemplateLookup(directories=tpldirectories,
                              output_encoding='utf-8', encoding_errors='replace')                      
        template = lookup.get_template(os.path.basename(path))
        self.response.content_type = 'text/html'
        css_dojo = getattr(self, '_css_dojo_d%s' % self.dojoversion)()
        gnrlibpath='gnr_d%s' % self.dojoversion
        
        dojolib=self.resolvePathAsUrl('dojo/dojo_%s/dojo/dojo.js'%self.dojoversion, folder='*lib')
        return template.render(mainpage=self,
                               css_genro = self.get_css_genro(gnrlibpath),

                               css_dojo = [self.resolvePathAsUrl('dojo/dojo_%s/%s' % (self.dojoversion,f), folder='*lib') for f in css_dojo],
                               dojolib=dojolib,
                               djConfig="parseOnLoad: false, isDebug: %s, locale: '%s'" % (self.isDeveloper() and 'true' or 'false',self.locale),
                               gnrModulePath='../../gnrjs',**kwargs)
        
    def rmlTemplate(self,path,inline=False,**kwargs):
        auth = self._checkAuth()
        if auth != AUTH_OK:
            self.raiseUnauthorized()
        tpldirectories=[os.path.dirname(path), self.parentdirpath]+self.resourceDirs+[self.resolvePath('gnrjs','gnr_d%s' % self.dojoversion,'tpl',folder='*lib')]
        lookup=TemplateLookup(directories=tpldirectories,
                             output_encoding='utf-8', encoding_errors='replace')                      
        template = lookup.get_template(os.path.basename(path))
        self.response.content_type = 'application/pdf'
        filename=os.path.split(path)[-1].split('.')[0]
        inline_attr=(inline and 'inline') or 'attachment'
        self.response.add_header("Content-Disposition",str("%s; filename=%s.pdf"%(inline_attr,filename)))
        import cStringIO
        from lxml import etree
        from z3c.rml import document
        tmp = template.render(mainpage=self,**kwargs)
        tmp=tmp.replace('&','&amp;')
        root = etree.fromstring(tmp)
        doc = document.Document(root)
        output = cStringIO.StringIO()
        doc.process(output)
        output.seek(0)
        return output.read()
        
    def debugger(self,debugtype,**kwargs):
        self.site.debugger(debugtype,_frame=sys._getframe(1),**kwargs)
        
    def rpc_bottomHelperContent(self):
        src = self.domSrcFactory.makeRoot(self)
        #src.data('debugger.main',Bang)
        sc=src.stackContainer()
        bc=sc.borderContainer()
        left=bc.contentPane(region='left',width='160px',background_color='silver',overflow='hidden').formbuilder(cols=1)
        left.checkBox(value='^debugger.sqldebug',label='Debug SQL')
        left.checkBox(value='^debugger.pydebug',label='Debug Python')
        left.button('Clear Debugger',action='genro.setData("debugger.main",null)')
        bc.contentPane(region='center').tree(storepath='debugger.main',isTree=False,fired='^debugger.tree_redraw',
                                             getIconClass="""return 'treeNoIcon';""",persist=False,inspect='shift')
        src.dataController("genro.debugopt=sqldebug?(pydebug? 'sql,py' :'sql' ):(pydebug? 'py' :null )",
                            sqldebug='^debugger.sqldebug',pydebug='^debugger.pydebug')
        src.dataController("FIRE debugger.tree_redraw;",sqldebug='^debugger.main',_delay=1)
        return src
    def rpc_debuggerContent(self):
        src = self.domSrcFactory.makeRoot(self)
        src.dataRemote('_dev.dbstruct','app.dbStructure')
        src.accordionPane(title='Datasource').tree(storepath='*D',persist=False,inspect='shift')
        src.accordionPane(title='Database').tree(storepath='_dev.dbstruct',persist=False,inspect='shift')
        src.accordionPane(title='Page source').tree(storepath='*S', label="Source inspector",
                                                   inspect='shift',selectedPath='_dev.selectedSourceNode') 
        src.dataScript('dummy','genro.src.highlightNode(fpath)',fpath='^_dev.selectedSourceNode')
        dbmnt=src.accordionPane(title='Db Maintenance')
        dbmnt.dataRpc('status', 'tableStatus', _fired='^aux.do_tableStatus')
        dbmnt.dataRpc('status', 'checkDb', _fired='^aux.do_checkDb')
        dbmnt.dataRpc('status', 'applyChangesToDb', _fired='^aux.do_applyChangesToDb')
        dbmnt.dataRpc('status', 'resetApp', _fired='^aux.do_resetApp')
        bc=dbmnt.borderContainer(height='100%')
        top=bc.contentPane(region='top',font_size='.9em',height='10ex')
        center=bc.tabContainer(region='center',font_size='.9em')
        center.contentPane(title='test')
        top.button('tableStatus', fire='aux.do_tableStatus',)
        top.button('CheckDb', fire='aux.do_checkDb')
        top.button('applyChangesToDb', fire='aux.do_applyChangesToDb')
        top.button('resetApp', fire='aux.do_resetApp')
        for k,x in enumerate(self.db.packages.items()):
            pkgname, pkg = x
            pane=center.contentPane(title=pkgname,height='100%')
            pane.button('test')
        return src
        
    def rpc_resetApp(self, **kwargs):
        self.siteStatus['resetTime'] = time.time()
        self.siteStatusSave()
        
    def rpc_applyChangesToDb(self, **kwargs):
        return self._checkDb(applychanges=True)
        
    def rpc_checkDb(self):
        return self._checkDb(applychanges=False)
        
    def _checkDb(self, applychanges=False, changePath=None, **kwargs):
        changes = self.application.checkDb()
        if applychanges:
            if changePath:
                changes = self.db.model.modelBagChanges.getAttr(changePath, 'changes')
                self.db.execute(changes)
            else:
                for x in self.db.model.modelChanges:
                    self.db.execute(x)
            self.db.commit()
            self.application.checkDb()
        return self.db.model.modelBagChanges
        
    def rpc_tableStatus(self,**kwargs):
        strbag = self._checkDb(applychanges=False)
        for pkgname, pkg in self.db.packages.items():
            for tablename in pkg.tables.keys():
                records=self.db.query('%s.%s' % (pkgname, tablename)).count()
                strbag.setAttr('%s.%s' %(pkgname,tablename), recordsnum=records)
        return strbag
        
    def createFileInData(self, *args):
        if args:
            path=os.path.join(self.siteFolder, 'data', *args)
            dirname=os.path.dirname(path)
            if not os.path.exists(dirname):
                os.makedirs(dirname)
            outfile=file(path, 'w')
            return outfile
           
    def createFileInStatic(self, *args):
        if args:
            path=os.path.join(self.siteFolder, 'pages','static', *args)
            dirname=os.path.dirname(path)
            if not os.path.exists(dirname):
                os.makedirs(dirname)
            outfile=file(path, 'w')
            return outfile
            
    def createFolderInData(self, *args):
        if args:
            path=os.path.join(self.siteFolder, 'data', *args)
            if not os.path.exists(path):
                os.makedirs(path)
            return path
    
    def createFolderInStatic(self, *args):
        if args:
            path=os.path.join(self.siteFolder, 'pages','static', *args)
            if not os.path.exists(path):
                os.makedirs(path)
            return path
            
    def getResourceUri(self, path, ext=None):
        fpath=self.getResource(path, ext=ext)
        if fpath:
            return self.diskPathToUri(fpath)
            
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

    def _get_resourceDirs(self):
        """Find a resource in current _resources folder or in parent folders one"""
        if not hasattr(self, '_resourceDirs'):
            pagesPath = self.folders['pages']
            curdir = self.folders['current']
            resourcePkg = None
            result = [] # result is now empty
            if self.packageId: # for index page or other pages at root level (out of any package)
                resourcePkg = self.package.attributes.get('resourcePkg')
                fpath = os.path.join(pagesPath, '_custom', self.packageId, '_resources')
                if os.path.isdir(fpath):
                    result.append(fpath) # we add a custom resource folder for current package
                
            fpath = os.path.join(pagesPath, '_custom', '_common_d11' , '_resources')
            
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
                    fpath = os.path.join(pagesPath, rp, '_resources')
                    if os.path.isdir(fpath):
                        result.append(fpath)
                        
            fpath = os.path.join(pagesPath, '_common_d11' , '_resources')
            if os.path.isdir(fpath):
                result.append(fpath) # we add a resource folder for common package
            self._resourceDirs = result
        # so we return a list of any possible resource folder starting from 
        # most customized and ending with most generic ones
        return self._resourceDirs 
    resourceDirs = property(_get_resourceDirs)
             
class GnrWebRpc(object):    
    def __call__(self, page, method=None, mode='bag', _auth=AUTH_FORBIDDEN, **kwargs):
        if _auth==AUTH_FORBIDDEN and method!='main':
            result = None
            error = 'forbidden call'
        elif _auth=='EXPIRED':
            result=None
            error='expired'
        else:
            handler=page.getPublicMethod('rpc', method)
            if method=='main':
                kwargs['_auth'] = _auth
            if handler:
                if page.debug_mode:
                    result = handler(**kwargs)
                    error=None
                else:
                    if True:
#                    try:
                        result = handler(**kwargs)
                        error = None
#                    except GnrWebClientError, err:
#                        result = err.args[0]
#                        error = 'clientError'
#                    except Exception, err:
#                        raise err
#                        result = page._errorPage(err,method,kwargs)
#                        mode='bag'
#                        error = 'serverError'

            else:
                result = None
                error = 'missing handler:%s' % method
        return getattr(self, '_call_%s' % mode.lower())(page, method, kwargs, result, error)
        
    def _call_bag(self, page, method, kwargs, result, error):
        envelope=Bag()
        resultAttrs={}
        dataChanges = page.clientDataChanges() or Bag()
        if isinstance(result,tuple):
            resultAttrs=result[1]
            if len(result)==3 and isinstance(result[2],Bag):
                #if dataChanges:
                dataChanges.update(result[2])
                #else:
                    #dataChanges = result[2]
            result=result[0]
            if resultAttrs is not None:
                envelope['resultType'] = 'node'
        if error:
            envelope['error'] = error
        if isinstance(result, page.domSrcFactory):
            resultAttrs['__cls']='domsource'
        if page.isLocalizer():
            envelope['_localizerStatus']='*_localizerStatus*'
        envelope.setItem('result', result, _attributes=resultAttrs)
        
        if page.debugopt and page._debug_calls:
            dataChanges.setItem('debugger_main',page._debug_calls,_client_path='debugger.main.c_%s'%page.callcounter)           
        if dataChanges :
            envelope.setItem('dataChanges', dataChanges)
        
        
        page.response.content_type = "text/xml"
        xmlresult= envelope.toXml(unresolved=True, jsonmode=True, jsonkey=page.page_id, 
                              translate_cb=page.translateText, omitUnknownTypes=True, catalog=page.catalog)
        if page.isLocalizer():
            _localizerStatus=''
            if hasattr(page,'_localizer'):
                if page.missingLoc:
                    _localizerStatus='missingLoc'
                else:
                    _localizerStatus='ok'
            xmlresult=xmlresult.replace('*_localizerStatus*', _localizerStatus)
        return xmlresult

    def _call_json(self, page, method, kwargs, result, error):
        if not error:
            return page.catalog.toJson(result)
        else:
            return page.catalog.toJson({'error':error})
        
    def _call_text(self, page, method, kwargs, result, error):
        return result or error
    
    def _call_html(self, page, method, kwargs, result, error):
        page.response.content_type = "text/html"
        return result or error

    
class GnrWebConnection(object):
    def __init__(self, page):
        self.page = page
        self.expired = False
        
    
    def initConnection(self):
        page = self.page
        self.cookieName = 'conn_%s' % self.page.siteName
        self.secret = page.config['secret'] or self.page.siteName
        self.allConnectionsFolder = os.path.join(self.page.siteFolder, 'data', '_connections')
        self.cookie = None
        self.oldcookie=None
        if page._user_login:
            user, password = page._user_login.split(':')
            self.connection_id = getUuid()
            avatar = page.application.getAvatar(user, password, authenticate=True,connection=self)
            self.cookie = self.page.newMarshalCookie(self.cookieName, {'connection_id': self.connection_id or getUuid(), 'slots':{}, 'locale':None, 'timestamp':None}, secret = self.secret)
            if avatar:
                self.updateAvatar(avatar)
        else:
            cookie = self.page.get_cookie(self.cookieName,'marshal', secret = self.secret)
            if cookie: #Cookie is OK
                self.oldcookie=cookie
                self.connection_id = cookie.value.get('connection_id')
                if self.connection_id:
                    cookie = self.verify(cookie)
                    if cookie:
                        self.cookie = cookie
            if not self.cookie:
                self.connection_id = getUuid()
                self.cookie = self.page.newMarshalCookie(self.cookieName, {'connection_id': self.connection_id, 'slots':{}, 'locale':None, 'timestamp':None}, secret = self.secret)

    def _get_data(self):
        if not hasattr(self, '_data'):
            if os.path.isfile(self.connectionFile):
                self._data = Bag(self.connectionFile)
            else:
                self._data = Bag()
                self._data['start.datetime'] = datetime.datetime.now()                
        return self._data
    data = property(_get_data)
    
    def cookieToRefresh(self):
        self.cookie.value['timestamp'] = None
        
    def _finalize(self):
        if not self.cookie.value.get('timestamp'):
            self.cookie.value['timestamp'] = time.time()
            self.data['ip'] = self.page.request.remote_addr
            self.data['pages'] = Bag(self.page.session.getActivePages(self.connection_id))
            self.write()
        self.cleanExpiredConnections(rnd=0.9)
        
    def writedata(self):
        """Write immediatly the disk file, not the cookie: use it for update data during a long process"""
        self.data.toXml(self.connectionFile, autocreate=True)

    def write(self):
        self.cookie.path = self.page.siteUri
        self.page.add_cookie(self.cookie)
        self.data['cookieData'] = Bag(self.cookie.value)
        self.data.toXml(self.connectionFile, autocreate=True)

    def _get_appSlot(self):
        if self.cookie:
            return self.cookie.value['slots'].setdefault(self.page.app.appId, {})
        return {}
    appSlot = property(_get_appSlot)
    
    def _get_locale(self):
        return self.cookie.value.get('locale')
    def _set_locale(self, v):
        self.cookie.value['timestamp'] = None
        self.cookie.value['locale'] = v
    locale = property(_get_locale, _set_locale)
    
    def updateAvatar(self, avatar):
        self.cookie.value['timestamp'] = None
        appSlot = self.appSlot
        appSlot['user'] = avatar.id
        appSlot['tags'] = avatar.tags

    def _get_connectionFolder(self):
        return os.path.join(self.allConnectionsFolder, self.connection_id)
    connectionFolder = property(_get_connectionFolder)

    def _get_connectionFile(self):
        return os.path.join(self.connectionFolder, 'connection.xml')
    connectionFile = property(_get_connectionFile)
    
    def rpc_logout(self,**kwargs):
        #self.cookie = self.page.newMarshalCookie(self.cookieName, {'expire':True,'connection_id': None, 'slots':{}, 'locale':None, 'timestamp':None}, secret = self.secret)
        self.close()
        
    def close(self):
        self.dropConnection(self.connection_id)
        
    def dropConnection(self,connection_id):
        self.page.site.connectionLog(self.page,'close')
        self.connFolderRemove(connection_id)
        
    def connFolderRemove(self, connection_id):
        path= os.path.join(self.allConnectionsFolder, connection_id)
        for root, dirs, files in os.walk(path, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir(path)
        
    def verify(self, cookie):
        if os.path.isfile(self.connectionFile):
            expire=False
            if cookie.value.get('expire'):
                expire=True
            elif cookie.value.get('timestamp'):
                cookieAge = time.time() - cookie.value['timestamp']
                if cookieAge < int(self.page.config.getItem('connection_refresh') or CONNECTION_REFRESH):
                    return cookie # fresh cookie
                elif cookieAge < int(self.page.config.getItem('connection_timeout') or CONNECTION_TIMEOUT):
                    cookie = self.page.newMarshalCookie(self.cookieName, {'connection_id': cookie.value.get('connection_id') or getUuid(), 
                                                                'locale':cookie.value.get('locale'),
                                                                 'slots':cookie.value.get('slots'), 'timestamp':None}, 
                                                                 secret = self.secret)
                    return cookie
                else:
                    expire=True
            if expire:
                self.isExpired = True
                #cookie = self.page.newMarshalCookie(self.cookieName, {'slots':cookie.value.get('slots'), 'timestamp':None}, secret = self.secret)
                self.close() # old cookie: destroy
                return cookie
                
    def cleanExpiredConnections(self, rnd=None):
        if (not rnd) or (random.random() > rnd):
            dirbag = self.connectionsBag()
            t = time.time()
            for conn_id, conn_files, abs_path in dirbag.digest('#k,#v,#a.abs_path'):
                try:
                    cookieAge = t - (conn_files['connection_xml.cookieData.timestamp'] or 0)
                except:
                    cookieAge = t
                    print conn_id
                if cookieAge > int(self.page.config.getItem('connection_timeout') or CONNECTION_TIMEOUT):
                    self.dropConnection(conn_id)
        
    def connectionsBag(self):
        if os.path.isdir(self.allConnectionsFolder):
            dirbag = Bag(self.allConnectionsFolder)['_connections']
        else:
            dirbag = Bag()
        return dirbag
            
    
class GnrWebSession(object):
    def __init__(self, page, sid=None, secret=None, timeout=None, lock=None):
        self.page_id = page.page_id
        kwargs=optArgs(sid=sid, secret=secret,timeout=timeout,lock=lock)
        #self.session = Session.Session(page.request, **kwargs)
        self.session = page.get_session(**kwargs)
        self.loadSessionData(False)
        self.locked = False
        
    def loadSessionData(self, locking=True):
        if locking and not self.locked:
            self.session.load()
            self.session.lock()
            self.locked = True
        self.pagedata = self.getSessionData(self.page_id)
        self.common = self.getSessionData('common')
        
    def saveSessionData(self):
        if not self.locked:
            raise
        self.pagedata.makePicklable()
        self.common.makePicklable()
        self.session.save()
        self.session.unlock()
        self.locked = False
        
    #def getActivePages(self, connection_id):
    #    result = {}
    #    for page_id, pagedata in self.session.items():
    #        if page_id != 'common' and pagedata['connection_id']==connection_id:
    #            result[page_id] = pagedata
    #    return result

    def getActivePages(self, connection_id):
        result = {}
        items=dict(self.session)
        if items.has_key('_accessed_time'): del items['_accessed_time']
        if items.has_key('_creation_time'): del items['_creation_time']
        for page_id, pagedata in items.items():
            if page_id != 'common' and pagedata['connection_id']==connection_id:
                result[page_id] = pagedata
        return result

    def setInPageData(self, path, value, _attributes=None, page_id=None, notifyClient=False):
        if not self.locked:
            self.loadSessionData()
        if (not page_id) or (page_id==self.page_id):
            self.pagedata.setItem(path, value, _attributes=_attributes)
        else:
            data = self.getSessionData(page_id)
            data.setItem(path, value, _attributes=_attributes)
            data.makePicklable()
            
    def modifyPageData(self, path, value, _attributes=None):
        self.loadSessionData()
        self.pagedata.setItem(path, value, _attributes=_attributes)
        self.saveSessionData()
        
    def setInCommonData(self, path, value, attr=None):
        self.common.setItem(path, value, attr)
                
    def removePageData(self):
        self.loadSessionData()
        self.session.pop(self.page_id)
        self.saveSessionData()
        
    def getSessionData(self, page_id):
        data = self.session.get(page_id)
        if data is None:
            data = Bag()
            self.session[page_id] = data
        else:
            data.restoreFromPicklable()
        return data
        
class GnrWebUtils(object):
    def __init__(self, page):
        #self._page=weakref.ref(page)
        self.page=page
        self.directory = page.sitepath
        self.filename = page.filename
        self.canonical_filename = page.canonical_filename
        
#    def _get_page(self):
#          if self._page:
#              return self._page()
#    page = property(_get_page)
      
    def siteFolder(self, *args,  **kwargs):
        """The http static root"""
        path = os.path.normpath(os.path.join(self.directory, '..', *args))
        relative=kwargs.get('relative')
        if relative:
            return self.diskPathToUri(path)
        return path
        
    def linkPage(self, *args, **kwargs):
        fromPage = kwargs.pop('fromPage')
        fromPageArgs = kwargs.pop('fromPageArgs')
        kwargs['relative'] = True
        topath = self.rootFolder(*args, **kwargs)
        if fromPage:
            fromPage = self.rootFolder(*args,**{'reverse':True})
            fromPage = '%s?%s' % (fromPage, urllib.urlencode(fromPageArgs))
            topath = '%s?%s' % (topath, urllib.urlencode({'fromPage':fromPage}))
        return topath

    def rootFolder(self, *args, **kwargs):
        """The mod_python root"""
        path = os.path.normpath(os.path.join(self.directory, *args))
        
        if kwargs.get('reverse'):
            return self.diskPathToUri(self.filename, fromfile=path)
        elif kwargs.get('relative'):
            return self.diskPathToUri(path)
        return path
        
    def pageFolder(self,*args,**kwargs):
        path = os.path.normpath(os.path.join(self.page.parentdirpath, *args))
        relative=kwargs.get('relative')
        if relative:
            return self.diskPathToUri(path)
        return path
        
    def relativePageFolder(self, *args, **kwargs):
        return os.path.dirname(self.canonical_filename).replace(self.page.siteFolder,'')
    
    def abspath(self, path):
        return os.path.normpath(os.path.join(os.path.dirname(self.filename), path))
    
    def absoluteDiskPath(self, path):
        os.path.join(self.page.siteFolder, path)
        return os.path.join(self.page.siteFolder, path)
    
    def diskPathToUri(self, tofile, fromfile=None):
        return self.page.diskPathToUri(tofile,fromfile=fromfile)
        fromfile = fromfile or self.filename
        basepath=os.path.normpath(os.path.join(self.directory, '..'))
        relUrl = tofile.replace(basepath,'').lstrip('/')
        path = fromfile.replace(basepath,'')
        rp = '../'*(len(path.split('/'))-2)
        return '%s%s' % (rp, relUrl)
        
    def readFile(self, path):
        if not path.startswith('/'):
            path=self.abspath(path)
        f=file(path,'r')
        result=f.read()
        f.close()
        return result
        
    def filename(self):
        return self.filename
     
    def dirbag(self, path='', base='', include='', exclude=None, ext=''):
        if base=='site':
            path = os.path.join(self.siteFolder, path)
        elif base=='root':
            path = os.path.join(self.rootFolder(), path)
        else:
            path = os.path.join(self.pageFolder(), path)
        
        result = Bag()
        path=os.path.normpath(path)
        path=path.rstrip('/')
        if not os.path.exists(path):
            os.makedirs(path)
        result[os.path.basename(path)] = DirectoryResolver(path, include=include, exclude=exclude, dropext=True, ext=ext)
        return result
        
    def pageTitle(self):
        return self.canonical_filename.replace(self.directory,'')
        
    def sendFile(self, content, filename=None, ext='', encoding='utf-8', mimetype='', sizelimit=200000):
        response = self.page.response
        if not mimetype:
            if ext=='xls':
                mimetype='application/vnd.ms-excel'
        filename = filename or self.page.request.uri.split('/')[-1]
        if encoding:
            content = content.encode(encoding)
        filename = filename.replace(' ','_').replace('/','-').replace(':','-').encode(encoding or 'ascii', 'ignore')
        if not sizelimit or len(content) < sizelimit:
            response.content_type = mimetype
            response.add_header("Content-Disposition", "attachment; filename=%s.%s" % (filename, ext))
        else:
            response.content_type = 'application/zip'
            response.add_header("Content-Disposition", "attachment; filename=%s.zip" % filename)
            zipresult = StringIO.StringIO()
            zip = zipfile.ZipFile(zipresult, mode='w', compression=zipfile.ZIP_DEFLATED)
            zipstring = zipfile.ZipInfo('%s.%s' % (filename, ext), datetime.datetime.now().timetuple()[:6])
            zipstring.compress_type = zipfile.ZIP_DEFLATED
            zip.writestr(zipstring, content)
            zip.close()
            content = zipresult.getvalue()
            zipresult.close()
        response.add_header("Content-Length", str(len(content)))
        response.write(content)
    
        
        

#-*- coding: UTF-8 -*-
#--------------------------------------------------------------------------
# package           : GenroPy web - see LICENSE for details
# module gnrwebcore : core module for genropy web framework
# Copyright (c)     : 2004 - 2007 Softwell sas - Milano 
# Written by        : Giovanni Porcari, Francesco Cavazzana
#                     Saverio Porcari, Francesco Porcari
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
import urllib
import itertools
from gnr.web._gnrbasewebpage import GnrBaseWebPage
import os
from gnr.core.gnrstring import toJson
from gnr.web.jsmin import jsmin
from gnr.core.gnrlang import getUuid
from mako.lookup import TemplateLookup
from gnr.web.gnrwebapphandler import GnrWsgiWebAppHandler
from gnr.core.gnrlang import GnrGenericException
from gnr.core.gnrhtml import GnrHtmlBuilder

CONNECTION_TIMEOUT = 3600
CONNECTION_REFRESH = 20
AUTH_OK=0
AUTH_NOT_LOGGED=1
AUTH_FORBIDDEN=-1

class GnrWebPageException(GnrGenericException):
    pass

class GnrWsgiPage(GnrBaseWebPage):
    
    def __init__(self, site, packageId=None,filepath=None):
        self.packageId=packageId
        self.filepath = filepath
        self.site = site
    
    def _get_config(self):
        return self.site.config
    config = property(_get_config)
    
    def index(self, theme=None, pagetemplate=None, **kwargs):
        self.onInit()
        if self._user_login:
            user=self.user # if we have an embedded login we get the user right now
        if True:
#        try:
            if 'mako' in kwargs:
                result = self.makoTemplate(path=kwargs['mako'], theme=theme, **kwargs)
            elif 'rml' in kwargs:
                result = self.rmlTemplate(path=kwargs['rml'], **kwargs)
            elif 'method' in kwargs:
                result = self._rpcDispatcher(**kwargs)
            else:
                result = self.indexPage(theme=theme,pagetemplate=pagetemplate,**kwargs)
                self.session.loadSessionData()
                self.session.pagedata['pageArgs'] = kwargs
                self.session.pagedata['page_id'] = self.page_id
                self.session.pagedata['connection_id'] = self.connection.connection_id
                self.session.pagedata['pagepath'] = self.pagepath
                self.session.saveSessionData()
#       except Exception, e:
#            self._onEnd()
#            raise e
        self._onEnd()
        return result
    
    def indexPage(self,theme=None,pagetemplate=None,**kwargs):
        self.theme = theme or 'tundra'
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
        return mytemplate.render(mainpage=self, **arg_dict)
    
    def makoTemplate(self, path, theme=None, striped='odd_row,even_row', pdf=False, **kwargs):
        self.theme = theme or 'tundra'
        auth = self._checkAuth()
        if auth != AUTH_OK:
            self.raiseUnauthorized()
        if striped:
            kwargs['striped']=itertools.cycle(striped.split(','))
        tpldirectories=[os.path.dirname(path), self.parentdirpath]+self.resourceDirs+[self.site.gnr_static_path(self.gnrjsversion,'tpl')]
        lookup=TemplateLookup(directories=tpldirectories,
                              output_encoding='utf-8', encoding_errors='replace')                      
        template = lookup.get_template(os.path.basename(path))
        css_dojo = getattr(self, '_css_dojo_d%s' % self.dojoversion)()
        
        _resources = self.site.resources.keys()
        _resources.reverse()
        dojolib = self.site.dojo_static_url(self.dojoversion,'dojo','dojo','dojo.js')
        gnrModulePath = self.site.gnr_static_url(self.gnrjsversion)
        self.js_requires.append(self.pagename)
        js_requires = [x for x in [self.getResourceUri(r,'js') for r in self.js_requires] if x]
        if os.path.isfile(self.resolvePath('%s.js' % self.pagename)):
            js_requires.append('%s.js' % self.pagename)
        css_requires, css_media_requires = self.get_css_requires()
        output = template.render(mainpage=self,
                               css_genro = self.get_css_genro(),
                               css_requires = css_requires , js_requires=self.js_requires,
                               css_media_requires = css_media_requires,
                               css_dojo = [self.site.dojo_static_url(self.dojoversion,'dojo',f) for f in css_dojo],
                               dojolib=dojolib,
                               djConfig="parseOnLoad: false, isDebug: %s, locale: '%s'" % (self.isDeveloper() and 'true' or 'false',self.locale),
                               gnrModulePath=gnrModulePath, **kwargs)
        if not pdf:
            self.response.content_type = 'text/html'
            return output
        else:
            from gnr.pdf.wk2pdf import WK2pdf
            import tempfile
            import sys
            self.response.content_type = 'application/pdf'
            tmp_name = self.temporaryDocument('tmp.pdf')
            if self.query_string:
                query_string = '&'.join([q for q in self.query_string.split('&') if not 'pdf' in q.lower()])
                url = '%s?%s'%(self.path_url,query_string)
            else:
                url = self.path_url
            wkprinter = WK2pdf(url,tmp_name)
            wkprinter.run()
            wkprinter.exec_()
            self.response.add_header("Content-Disposition",str("%s; filename=%s.pdf"%('inline',self.path_url.split('/')[-1]+'.pdf')))
            tmp_file = open(tmp_name)
            tmp_content = tmp_file.read()
            tmp_file.close()
            return tmp_content
            
    
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
        arg_dict['startArgs'] = toJson(kwargs)
        arg_dict['page_id'] = self.page_id or getUuid()
        arg_dict['bodyclasses'] = self.get_bodyclasses()
        arg_dict['dojolib'] = dojolib
        arg_dict['djConfig'] = "parseOnLoad: false, isDebug: %s, locale: '%s'" % (self.isDeveloper() and 'true' or 'false',self.locale)
        arg_dict['gnrModulePath'] = gnrModulePath
        gnrimports = getattr(self, '_gnrjs_d%s' % self.dojoversion)()
        if self.site.debug or self.isDeveloper():
            arg_dict['genroJsImport'] = [self.site.gnr_static_url( self.gnrjsversion,'js', '%s.js' % f) for f in gnrimports]
        else:
            jsfiles = [self.site.gnr_static_path(self.gnrjsversion,'js', '%s.js' % f) for f in gnrimports]
            arg_dict['genroJsImport'] = [self._jscompress(jsfiles)]
        css_dojo = getattr(self, '_css_dojo_d%s' % self.dojoversion)()
        arg_dict['css_dojo'] = [self.site.dojo_static_url(self.dojoversion,'dojo',f) for f in css_dojo]
        arg_dict['css_genro'] = self.get_css_genro()
        self.js_requires.append(self.pagename)
        js_requires = [x for x in [self.getResourceUri(r,'js') for r in self.js_requires] if x]
        if os.path.isfile(self.resolvePath('%s.js' % self.pagename)):
            js_requires.append('%s.js' % self.pagename)
        arg_dict['js_requires'] = js_requires
        css_requires = self.get_css_requires()
        #if os.path.isfile(self.resolvePath('%s.css' % self.pagename)):
        #    css_requires.append('%s.css' % self.pagename)
        css_requires, css_media_requires = self.get_css_requires()
        arg_dict['css_requires'] = css_requires
        arg_dict['css_media_requires'] = css_media_requires
        return arg_dict
    
    def homeUrl(self):
        return self.site.home_uri
        
    def getDomainUrl(self, path='', **kwargs):
        params = urllib.urlencode(kwargs)
        path =  '%s/%s'%(self.homeUrl,path.lstrip('/'))
        if params:
            path = '%s?%s' % (path, params)
        return path

    def get_bodyclasses(self):
        return '%s _common_d11 pkg_%s page_%s' % (self.theme, self.packageId, self.pagename)
    
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
            self._app = GnrWsgiWebAppHandler(self)
        return self._app
    app = property(_get_app) #cambiare in appHandler e diminuirne l'utilizzo al minimo

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
    
    def checkPermission(self, pagepath, relative=True):
        return self.application.checkResourcePermission(self.auth_tags, self.userTags)
    
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
    
    def get_css_requires(self):
        filepath = os.path.splitext(self.filepath)[0]
        css_requires = []
        css_media_requires = {}
        for css in self.css_requires:
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
                page.data('_server', None, context='_server')
                page.dataController('genro.dlg.alert(msg);', msg='^gnr.alert')
                page.dataController('genro.rpc.managePolling(freq);', freq='^gnr.polling', _fired='^gnr.onStart')
                morePars={}
                
                root=page.borderContainer(design='sidebar', height='100%', nodeId='_gnrRoot', regions='^_clientCtx.mainBC')
                root.dataController("SET _clientCtx.mainBC.right?show=false;",_init=True)
                root.dataController("if(show){genro.nodeById('gnr_debugger').updateContent();}",show='^_clientCtx.mainBC.right?show')
                debugAc = root.accordionContainer(width='20%',region='right',splitter=True, nodeId='gnr_debugger')
                debugAc.remote('debuggerContent', cacheTime=-1)
                self.mainLeftContent(root,region='left',splitter=True, nodeId='gnr_main_left')
                rootwdg = self.rootWidget(root, region='center', nodeId='_pageRoot')
                self.main(rootwdg, **kwargs)
                self.onMainCalls()
                self._createContext(root)
            elif _auth==AUTH_NOT_LOGGED:
                loginUrl = self.application.loginUrl()
                page = None
                if loginUrl:
                    pageattr['redirect'] = self.resolvePathAsUrl(loginUrl,folder='*pages')
                else:
                    pageattr['redirect'] = self.resolvePathAsUrl('simplelogin.py',folder='*common')
            else:
                self.forbiddenPage(page, **kwargs)
            return (page, pageattr)
            #except Exception,err:
        else:
            return (self._errorPage(err), pageattr)
            
    def loadTableResource(self, table,restype, respath, class_name='Main'):
        return self.site.loadTableResource(self, table=table,path='%s/%s:%s' % (restype,respath,class_name))
        
    def rpc_tableResource(self,table, restype, respath, class_name='Main',method='run',**kwargs):
        instance=self.loadTableResource(table=table,restype=restype,respath=respath,class_name=class_name)
        handler=getattr(instance, 'rpc_%s' % method)
        return handler(**kwargs)
            
class GnrMakoPage(GnrWsgiPage):
    def index(self,*args, **kwargs):
        return GnrWsgiPage.index(self,*args, mako=self.mako_template(),**kwargs)
        
class GnrHtmlPage(GnrWsgiPage):
    
    def __init__(self, site, packageId=None,filepath=None):
        self.packageId=packageId
        self.filepath = filepath
        self.site = site
        self.builder = GnrHtmlBuilder()
        
    def main(self, *args, **kwargs):
        pass
        
    
    def dojo(self, version=None, theme='tundra'):
        self.theme = theme
        version = version or self.dojoversion
        djConfig="parseOnLoad: true, isDebug: %s, locale: '%s'" % (self.isDeveloper() and 'true' or 'false',self.locale)
        css_dojo = getattr(self, '_css_dojo_d%s' % version)()
        import_statements = ';\n'.join(['@import url("%s")'%self.site.dojo_static_url(self.dojoversion,'dojo',f) for f in css_dojo])
        self.builder.head.style(import_statements+';', type="text/css")
        
        self.body.script(src=self.site.dojo_static_url(version,'dojo','dojo','dojo.js'), djConfig=djConfig)
    
    def gnr_css(self):
        css_genro = self.get_css_genro()
        for css_media,css_link in css_genro.items():
            import_statements = ';\n'.join(css_link)
            self.builder.head.style(import_statements+';', type="text/css", media=css_media)
    
    def index(self, *args, **kwargs):
        for popkey in ('theme', 'pagetemplate'):
            if popkey in kwargs:
                kwargs.pop(popkey)
        self.builder.initializeSrc()
        self.body = self.builder.body
        self.main(self.body,*args, **kwargs)
        return self.builder.toHtml()
        
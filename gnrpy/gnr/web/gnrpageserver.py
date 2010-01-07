#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  untitled
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#
from gnr.core.gnrbag import Bag, DirectoryResolver
import os

class PageServer(object):
    def __init__(self, site=None):
        self.site = site
        self.site_path = self.site.site_path
        self.gnrapp = self.site.gnrapp
        self.build_automap()
        self.page_factories={}
    
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
        for package in self.site.gnrapp.packages.values():
            packagemap = DirectoryResolver(os.path.join(package.packageFolder, 'webpages'),
                                             include='*.py',exclude='_*,.*')()
            packagemap.walk(handleNode,_mode='',pkg=package.id)
            self.automap.setItem(package.id, packagemap,name=package.attributes.get('name_long') or package.id)
        self.automap.toXml(os.path.join(self.site_path,'automap.xml'))

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
    
    def get_page_node(self, path_list):
        # get the deepest node in the sitemap bag associated with the given url
        page_node = self.sitemap.getDeepestNode('.'.join(path_list))
        if self.site.mainpackage and not page_node: # try in the main package
            page_node = self.sitemap.getDeepestNode('.'.join([self.site.mainpackage]+path_list))
        if page_node:
            page_node_attributes = page_node.getInheritedAttributes()
            if not page_attr.get('path'):
                page_node = self.sitemap.getDeepestNode('.'.join(path_list+['index']))
                page_node_attributes = page_node.getInheritedAttributes()
                if page_attr.get('path'):
                    page_args = page_node._tail_path.split('.')
                    return page_node, page_node_attributes, page_args
        return None,None,None

    
    def __call__(self, path_list, environ, start_response, req):
        t=time()
        page_kwargs=dict(req.params)
        page_node, page_node_attributes, page_args = self.get_page_node(path_list)
        if not page_node:
            return self.not_found(environ,start_response)
        if self.debug:
            page = self.page_create(**page_node_attributes)
        else:
            try:
                page = self.page_create(**page_node_attributes)
            except Exception,exc:
                raise exc
        if not page:
            return self.not_found(environ,start_response)
        self.site.currentPage = page
        self.page_init(page,request=req, response=resp, page_kwargs=page_kwargs)
        if page_args:
            page_args=page.handleSubUrl(page_args.split('.'))
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
        self.db.closeConnection()
        return resp(environ, start_response)
    
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

    def page_init(self,page, request=None, response=None, page_kwargs=None):
        for attr in ['page_id', '_rpc_resultPath', '_user_login', 'debug']:
            setattr(page,attr,page_kwargs.pop('_rpc_resultPath',None))
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
        page.debug_mode = self.debug and True or False
        page._dbconnection=None

    def get_page_factory(self, path, pkg = None, rel_path=None):
        if path in self.page_factories:
            return self.page_factories[path]
        page_module = gnrImport(path,avoidDup=True)
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
        classMixin(page_class,custom_class, only_callables=False)
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
            classMixin(page_class,package.webPageMixin, only_callables=False) # first the package standard
        if self.gnrapp.webPageCustom:
            classMixin(page_class,self.gnrapp.webPageCustom, only_callables=False) # then the application custom
        if package and package.webPageMixinCustom:
            classMixin(page_class,package.webPageMixinCustom, only_callables=False) # finally the package custom


    def page_class_custom_mixin(self,page_class, path, pkg=None):
        """Look in the instance custom folder for a file named as the current webpage"""
        path=path.split(os.path.sep)
        if pkg:
            customPagePath=os.path.join(self.gnrapp.customFolder, pkg, 'webpages', *path)
            if os.path.isfile(customPagePath):
                component_page_module = gnrImport(customPagePath,avoidDup=True)
                component_page_class = getattr(component_page_module,'WebPage',None)
                if component_page_class:
                    classMixin(page_class, component_page_class, only_callables=False)

    def page_pyrequires_mixin(self, page_class, py_requires):
        for mix in py_requires:
            if mix:
                self.mixinResource(page_class, page_class._resourceDirs, mix)

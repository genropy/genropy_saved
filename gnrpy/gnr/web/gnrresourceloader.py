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
from gnr.core.gnrlang import gnrImport, classMixin, cloneClass
from gnr.core.gnrstring import splitAndStrip
from gnr.web.gnrwebpage import GnrWebPage
from gnr.web.gnrbaseclasses import BaseResource


class GnrMixinError(Exception):
    pass

class ResourceLoader(object):
    def __init__(self, site=None):
        self.site = site
        self.site_path = self.site.site_path
        self.gnrapp = self.site.gnrapp
        self.debug = self.site.debug
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
        if not page_node and self.site.mainpackage : # try in the main package
            page_node = self.sitemap.getDeepestNode('.'.join([self.site.mainpackage]+path_list))
        if page_node:
            page_node_attributes = page_node.getInheritedAttributes()
            if page_node_attributes.get('path'):
                return page_node, page_node_attributes
            else:
                page_node = self.sitemap.getDeepestNode('.'.join(path_list+['index']))
                if page_node:
                    page_node_attributes = page_node.getInheritedAttributes()
                    if page_node_attributes.get('path'):
                        return page_node, page_node_attributes
        return None,None

    
    def __call__(self, path_list, request, response):
        page_node, page_node_attributes = self.get_page_node(path_list)
        if not page_node:
            return None
        request_args = page_node._tail_list
        path = page_node_attributes.get('path')
        pkg = page_node_attributes.get('pkg')
        page_class = self.get_page_class(path = path, pkg = pkg)
        page = page_class(site= self.site, request=request, response=response, request_kwargs=dict(request.params), request_args=request_args,
                    filepath = path, packageId = pkg, basename = path)
        return page
 
    def get_page_class(self,path=None,pkg=None):
        if pkg=='*':
            module_path = os.path.join(self.site_path,path)
            pkg = self.site.config['packages?default']
        else:
            module_path = os.path.join(self.gnrapp.packages[pkg].packageFolder,'webpages',path)
        
        if module_path in self.page_factories:
            return self.page_factories[module_path]
        page_module = gnrImport(module_path,avoidDup=True)
        page_factory = getattr(page_module,'page_factory',GnrWebPage)
        custom_class = getattr(page_module,'GnrCustomWebPage')
        py_requires = splitAndStrip(getattr(custom_class, 'py_requires', '') ,',')
        page_class = cloneClass('GnrCustomWebPage',page_factory)
        page_class.__module__ = page_module
        self.page_class_base_mixin(page_class, pkg=pkg)
        page_class.dojoversion = getattr(custom_class, 'dojoversion', None) or self.site.config['dojo?version'] or '11'
        page_class.theme = getattr(custom_class, 'theme', None) or self.site.config['dojo?theme'] or 'tundra'
        page_class.gnrjsversion = getattr(custom_class, 'gnrjsversion', None) or self.site.config['gnrjs?version'] or '11'
        page_class.maintable = getattr(custom_class, 'maintable', None)
        page_class.recordLock = getattr(custom_class, 'recordLock', None)
        page_class.polling = getattr(custom_class, 'polling', None)
        page_class.eagers = getattr(custom_class, 'eagers', {})
        page_class.css_requires = splitAndStrip(getattr(custom_class, 'css_requires', ''),',')
        page_class.js_requires = splitAndStrip(getattr(custom_class, 'js_requires', ''),',')
        page_class.pageOptions = getattr(custom_class,'pageOptions',{})
        page_class.auth_tags = getattr(custom_class, 'auth_tags', '')
        self.page_class_resourceDirs(page_class, module_path, pkg=pkg)
        self.page_pyrequires_mixin(page_class, py_requires)
        classMixin(page_class,custom_class, only_callables=False)
        self.page_class_resourceDirs(page_class, module_path, pkg=pkg)
        page_class._packageId = pkg
        self.page_class_custom_mixin(page_class, path, pkg=pkg)
        self.page_factories[module_path]=page_class
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
        resources_list = self.site.resources_dirs
        result.extend(resources_list)
        page_class.tpldirectories=result+[self.site.gnr_static_path(page_class.gnrjsversion,'tpl')]
        page_class._resourceDirs = result

    def page_pyrequires_mixin(self, page_class, py_requires):
        for mix in py_requires:
            if mix:
                self.mixinResource(page_class, page_class._resourceDirs, mix)

    def mixinResource(self, kls,resourceDirs,*path):
        path = os.path.join(*path)
        if ':' in path:
            modName, clsName = path.split(':')
        else:
            modName, clsName = path,'*'
        modPathList = self.site.getResourceList(resourceDirs, modName, 'py') or []
        if modPathList:
            modPathList.reverse()
            for modPath in modPathList:
                classMixin(kls,'%s:%s'%(modPath,clsName),only_callables=False,site=self)
        else:
            raise GnrMixinError('Cannot import component %s' % modName)


    def loadResource(self,pkg, *path):
        resourceDirs = self.gnrapp.packages[pkg].resourceDirs
        resource_class = cloneClass('CustomResource',BaseResource)
        self.mixinResource(resource_class, resourceDirs, *path)
        return resource_class()

#!/usr/bin/env pythonw
# -*- coding: utf-8 -*-
#
#  gnrresourceloader.py
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.

from gnr.core.gnrbag import Bag, DirectoryResolver
import os
import re
import inspect
import glob
import logging

from gnr.core.gnrlang import gnrImport, classMixin, cloneClass,clonedClassMixin
from gnr.core.gnrstring import splitAndStrip
from gnr.core.gnrsys import expandpath
from gnr.web.gnrwebpage import GnrWebPage
from gnr.web._gnrbasewebpage import GnrWebServerError
from gnr.web.gnrbaseclasses import BaseResource
from gnr.web.gnrbaseclasses import BaseWebtool
from gnr.core.gnrclasses import GnrMixinError,GnrMixinNotFound
from gnr.core.gnrlang import uniquify


log = logging.getLogger(__name__)




class ResourceLoader(object):
    """Base class to load :ref:`intro_resources`"""
    def __init__(self, site=None):
        self.site = site
        self.site_path = self.site.site_path
        self.site_name = self.site.site_name
        self.gnr_config = self.site.gnr_config
        self.debug = self.site.debug
        self.gnr_static_handler = self.site.getStatic('gnr')
        self.page_factories = {}
        self.default_path = self.site.default_page and self.site.default_page.split('/')
    
    @property
    def gnrapp(self):
        return self.site.gnrapp

    def find_webtools(self):
        """TODO"""
        def isgnrwebtool(cls):
            return inspect.isclass(cls) and issubclass(cls, BaseWebtool) and cls is not BaseWebtool
            
        tools = {}
        webtool_pathlist = []
        if 'webtools' in self.gnr_config['gnr.environment_xml']:
            for path in self.gnr_config['gnr.environment_xml'].digest('webtools:#a.path'):
                webtool_pathlist.append(expandpath(path))
        for package in self.gnrapp.packages.values():
            webtool_pathlist.append(os.path.join(package.packageFolder, 'webtools'))
        project_resource_path = os.path.join(self.site_path, '..', '..', 'webtools')
        webtool_pathlist.append(os.path.normpath(project_resource_path))
        for path in webtool_pathlist:
            if not os.path.isdir(path):
                continue
            for tool_module in os.listdir(path):
                if tool_module.endswith('.py'):
                    module_path = os.path.join(path, tool_module)
                    try:
                        module = gnrImport(module_path, avoidDup=True)
                        tool_classes = inspect.getmembers(module, isgnrwebtool)
                        tool_classes = [(name.lower(), value) for name, value in tool_classes]
                        tools.update(dict(tool_classes))
                    except ImportError:
                        pass
        return tools

    def __call__(self, path_list, request, response, environ=None,request_kwargs=None):
        request_kwargs = request_kwargs or dict()
        info = self.site.getUrlInfo(path_list,request_kwargs,default_path=self.default_path)
        if not info.relpath:
            return None
        _avoid_module_cache = request_kwargs.pop('_avoid_module_cache', None)

        page_class = self.get_page_class(basepath=info.basepath,relpath=info.relpath, pkg=info.pkg,
                                        avoid_module_cache=_avoid_module_cache,
                                        request_args=info.request_args,request_kwargs=request_kwargs)
        class_info = dict(basepath=info.basepath,relpath=info.relpath, pkg=info.pkg,
                            request_args=info.request_args,request_kwargs=request_kwargs)
        page = page_class(site=self.site, request=request, response=response,
                          request_kwargs=request_kwargs, request_args=info.request_args,
                          filepath=info.relpath, packageId=page_class._packageId, 
                          pluginId=info.plugin,  basename=info.relpath, environ=environ, class_info=class_info,
                          _avoid_module_cache=_avoid_module_cache)
        return page

    def get_page_by_id(self, page_id):
        page_item = self.site.register.page(page_id,include_data='lazy')
        if not page_item:
            return
        class_info = page_item['data']['class_info']
        init_info = page_item['data']['init_info']
        page_info = page_item['data']['page_info']
        return self.instantiate_page(page_id=page_id,class_info=class_info, init_info=init_info, page_info=page_info)

    def instantiate_page(self, page_id=None,class_info=None, init_info=None, page_info=None, mixin_set=None):
        from gnr.web.gnrsimplepage import GnrSimplePage
        
        class_info['page_factory'] = GnrSimplePage
        page_class = self.get_page_class(**class_info)
        page = page_class(site=self.site, page_id=page_id,page_info=page_info, **init_info)
        page.replayComponentMixins(mixin_set=mixin_set)
        return page


    def get_page_class(self, basepath=None,relpath=None, pkg=None, plugin=None,avoid_module_cache=None,request_args=None,request_kwargs=None, page_factory=None):
        """TODO
        
        :param path: TODO
        :param pkg: the :ref:`package <packages>` object"""

        module_path = os.path.join(basepath,relpath)
        page_module = gnrImport(module_path, avoidDup=True,silent=False,avoid_module_cache=avoid_module_cache)
        page_factory = page_factory or getattr(page_module, 'page_factory', GnrWebPage)
        custom_class = getattr(page_module, 'GnrCustomWebPage')
        mainPkg = pkg
        if hasattr(custom_class,'getMainPackage'):
            kw = dict()
            if 'page_id' in request_kwargs:
                kw = self.site.register.pageStore(request_kwargs['page_id']).getItem('pageArgs') or dict()
                kw.update(request_kwargs)
            mainPkg = custom_class.getMainPackage(request_args=request_args,request_kwargs=kw)
        py_requires = splitAndStrip(getattr(custom_class, 'py_requires', ''), ',')
        plugin_webpage_classes = self.plugin_webpage_classes(relpath, pkg=mainPkg)
        for plugin_webpage_class in plugin_webpage_classes:
            plugin_py_requires = splitAndStrip(getattr(plugin_webpage_class, 'py_requires', ''), ',')
            py_requires.extend(plugin_py_requires)
        page_class = cloneClass('GnrCustomWebPage', page_factory)
        page_class.__module__ = page_module.__name__
        self.page_class_base_mixin(page_class, pkg=mainPkg)
        package_py_requires = splitAndStrip(getattr(page_class, 'package_py_requires', ''), ',')
        package_js_requires = splitAndStrip(getattr(page_class, 'package_js_requires', ''), ',')
        package_css_requires = splitAndStrip(getattr(page_class, 'package_css_requires', ''), ',') 
        if package_py_requires:
            py_requires = uniquify(package_py_requires + py_requires)
        page_class.dojo_version = getattr(custom_class, 'dojo_version', None) or self.site.config[
                                                                                 'dojo?version'] or '11'
        page_class.theme = getattr(custom_class, 'theme', None) or self.site.config['dojo?theme'] or 'tundra'
        page_class.gnrjsversion = getattr(custom_class, 'gnrjsversion', None) or self.site.config[
                                                                                 'gnrjs?version'] or '11'
        page_class.maintable = getattr(custom_class, 'maintable', None)
        page_class.recordLock = getattr(custom_class, 'recordLock', None)
        page_class.user_polling = int(
                getattr(custom_class, 'user_polling', None) or self.site.config['polling?user'] or 3)
        page_class.auto_polling = int(
                getattr(custom_class, 'auto_polling', None) or self.site.config['polling?auto'] or 30)
        if hasattr(custom_class,'polling_enabled'):
            page_class.polling_enabled = getattr(custom_class, 'polling_enabled')
        page_class.eagers = getattr(custom_class, 'eagers', {})
        page_class.css_requires = []
        page_class.js_requires = splitAndStrip(getattr(custom_class, 'js_requires', ''), ',')
        if package_js_requires:
            page_class.js_requires = uniquify(package_js_requires + page_class.js_requires)
        page_class.pageOptions = getattr(custom_class, 'pageOptions', {})
        page_class.auth_tags = getattr(custom_class, 'auth_tags', '')
        page_class.resourceDirs = self.page_class_resourceDirs(page_class, module_path, pkg=mainPkg)
        self.page_pyrequires_mixin(page_class, py_requires)
        classMixin(page_class, custom_class, only_callables=False)
        page_class.css_requires.extend([x for x in splitAndStrip(getattr(custom_class, 'css_requires', ''), ',') if x])
        if package_css_requires:
            page_class.css_requires = uniquify(page_class.css_requires+package_css_requires)
        page_class.tpldirectories = page_class.resourceDirs + [
                self.gnr_static_handler.path(page_class.gnrjsversion, 'tpl')]
        page_class._packageId = mainPkg
        self.page_class_plugin_mixin(page_class, plugin_webpage_classes)
        self.page_class_custom_mixin(page_class, relpath, pkg=mainPkg)
        self.page_factories[module_path] = page_class
        return page_class
        
    def page_class_base_mixin(self, page_class, pkg=None):
        """Look for custom classes in the package
        
        :param page_class: TODO
        :param pkg: the :ref:`package <packages>` object"""
        package = None
        if pkg:
            package = self.gnrapp.packages[pkg]
        if package and package.webPageMixin:
            classMixin(page_class, package.webPageMixin, only_callables=False) # first the package standard
        if self.gnrapp.webPageCustom:
            classMixin(page_class, self.gnrapp.webPageCustom, only_callables=False) # then the application custom
        if package and package.webPageMixinCustom:
            classMixin(page_class, package.webPageMixinCustom, only_callables=False) # finally the package custom
            
    def plugin_webpage_classes(self, path, pkg=None):
        """Look in the plugins folders for a file named as the current webpage and get all classes
        
        :param path: TODO
        :param pkg: the :ref:`package <packages>` object"""
        plugin_webpage_classes = []
        path = path.split(os.path.sep)
        pkg = pkg and self.site.gnrapp.packages[pkg]
        if pkg:
            pkg_plugins = pkg.getPlugins()
            for plugin in pkg_plugins:
                pluginPagePath = os.path.join(plugin.webpages_path, *path)
                if os.path.isfile(pluginPagePath):
                    component_page_module = gnrImport(pluginPagePath, avoidDup=True)
                    component_page_class = getattr(component_page_module, 'GnrCustomWebPage', None)
                    if component_page_class:
                        plugin_webpage_classes.append(component_page_class)
        return plugin_webpage_classes
        
    def page_class_plugin_mixin(self, page_class, plugin_webpage_classes):
        """Mixin the current class with the *plugin_webpage_classes* attribute
        
        :param page_class: TODO
        :param plugin_webpage_classes: TODO"""
        for plugin_webpage_class in plugin_webpage_classes:
            classMixin(page_class, plugin_webpage_class, only_callables=False)
            
    def page_class_custom_mixin(self, page_class, path, pkg=None):
        """Look in the instance custom folder for a file named as the current webpage
        
        :param page_class: TODO
        :param path: TODO
        :param pkg: the :ref:`package <packages>` object"""
        path = path.split(os.path.sep)
        if pkg:
            customPagePath = os.path.join(self.gnrapp.customFolder, pkg, 'webpages', *path)
            if os.path.isfile(customPagePath):
                component_page_module = gnrImport(customPagePath, avoidDup=True)
                component_page_class = getattr(component_page_module, 'WebPage', None)
                if component_page_class:
                    classMixin(page_class, component_page_class, only_callables=False)
    
    def _appendPathIfExists(self,result, path):
        if os.path.exists(path):
            result.append(path)
                    
    def page_class_resourceDirs(self, page_class, path, pkg=None):
        """Build page resources directories
        
        :param page_class: TODO
        :param path: TODO
        :param pkg: the :ref:`package <packages>` object"""

        if pkg:
            currentAuxInstanceName = self.site.currentAuxInstanceName
            pagesPath = os.path.join(self.gnrapp.packages[pkg].packageFolder, 'webpages')
            packageResourcePath =  os.path.join(self.gnrapp.packages[pkg].packageFolder, 'resources')
        else:
            pagesPath = os.path.join(self.site_path, 'pages')
            packageResourcePath = None
        #curdir = os.path.dirname(os.path.join(pagesPath, path))
        #resourcePkg = None
        result = [] # result is now empty
        fpath = os.path.join(self.site_path, 'resources')
        self._appendPathIfExists(result, fpath) # we add a custom resource folder for current package
        if pkg: # for index page or other pages at root level (out of any package)
            #resourcePkg = self.gnrapp.packages[pkg].attributes.get('resourcePkg')
            fpath = os.path.join(self.site_path, '_custom', pkg, '_resources')
            self._appendPathIfExists(result, fpath) # we add a custom resource folder for current package
        
        fpath = os.path.join(self.site_path, '_resources')
        self._appendPathIfExists(result, fpath) # we add a custom resource folder for common package
            
        #while curdir.startswith(pagesPath):
        #    fpath = os.path.join(curdir, '_resources')
        #    if os.path.isdir(fpath):
        #        result.append(fpath)
        #    curdir = os.path.dirname(curdir) # we add a resource folder for folder 
            # of current page
        #if resourcePkg:
        #    for rp in resourcePkg.split(','):
        #        fpath = os.path.join(self.gnrapp.packages[rp].packageFolder, 'webpages', '_resources')
        #        if os.path.isdir(fpath):
        #            result.append(fpath)
            #result.extend(self.siteResources)
        if packageResourcePath:
            self._appendPathIfExists(result, packageResourcePath)
        resources_list = self.site.resources_dirs
        result.extend(resources_list)
        return result
        
    def package_resourceDirs(self, pkg, omitSiteResources=False, pluginId=None):
        """TODO
        
        :param pkg: the :ref:`package <packages>` object
        :param omitSiteResources: boolean. TODO"""
        pkg = self.gnrapp.packages[pkg]
        result = []
        if not hasattr(pkg, '_resourceDirs'):
            resourcePkg = None
            pkgResourceDirs = [] # result is now empty
            resourcePkg = pkg.attributes.get('resourcePkg')
            fpath = os.path.join(self.site_path, '_custom', pkg.id, '_resources')
            if os.path.isdir(fpath):
                pkgResourceDirs.append(fpath) # we add a custom resource folder for current package
                
            if resourcePkg:
                for rp in resourcePkg.split(','):
                    fpath = os.path.join(self.site_path, '_custom', pkg.id, '_resources')
                    if os.path.isdir(fpath):
                        pkgResourceDirs.append(fpath)
            rsrc_path = os.path.join(pkg.packageFolder, 'resources')
            if os.path.isdir(rsrc_path):
                pkgResourceDirs.append(rsrc_path)
            pkg._siteResourceDirs = self.site.resources_dirs
            pkg._resourceDirs = pkgResourceDirs
        result.extend(list(pkg._resourceDirs))
        if not omitSiteResources:
            result.extend(pkg._siteResourceDirs)
            # so we return a list of any possible resource folder starting from
        # most customized and ending with most generic ones
        return result
        
    def site_resources(self):
        """TODO"""
        resources = Bag()
        resources['site'] = os.path.join(self.site_path, 'resources')
        resources_list = [(resource.label, resource.attr.get('path')) for resource in
                          self.site.config['resources'] or []]
        for label, rsrc_path in resources_list:
            if rsrc_path:
                resources[label] = rsrc_path
            else:
                rsrc_path = self.resource_name_to_path(label)
                resources[label] = rsrc_path
        auto_resource_path = self.resource_name_to_path(self.site_name, safe=False)
        if auto_resource_path:
            resources[self.site_name] = os.path.realpath(auto_resource_path)

        for pkg in self.site.gnrapp.packages.values():
            rsrc_path = os.path.join(pkg.packageFolder, 'resources')
            label = 'pkg_%s' % (pkg.id)
            if os.path.isdir(rsrc_path):
                resources[label] = rsrc_path
            plugins = [p for p in pkg.getPlugins() if p.resources_path]
            for plugin in plugins:
                label = 'pkg_%s_%s' % (pkg.id,plugin.id)
                if os.path.isdir(plugin.resources_path):
                    resources[label] = plugin.resources_path
        return resources
        
    def resource_name_to_path(self, res_id, safe=True):
        """TODO
        
        :param res_id: TODO
        :param safe: TODO"""
        project_resource_path = os.path.normpath(os.path.join(self.site_path, '..', '..', 'resources', res_id))
        if os.path.isdir(project_resource_path):
            log.debug('resource_name_to_path(%s) -> %s (project)' % (repr(res_id),repr(project_resource_path)))
            return project_resource_path
        if 'resources' in self.gnr_config['gnr.environment_xml']:
            for path in self.gnr_config['gnr.environment_xml'].digest('resources:#a.path'):
                res_path = expandpath(os.path.join(path, res_id))
                if os.path.isdir(res_path):
                    log.debug('resource_name_to_path(%s) -> %s (gnr config)' % (repr(res_id), repr(res_path)))
                    return res_path
        log.debug('resource_name_to_path(%s) not found.' % repr(res_id))
        if safe:
            raise Exception('Error: resource %s not found' % res_id)
            
    def page_pyrequires_mixin(self, page_class, py_requires):
        """Allow to mixin the :ref:`webpage python requirements <webpages_py_requires>`
        
        :param page_class: TODO
        :param py_requires: TODO"""
        for mix in py_requires:
            if mix:
                self.mixinResource(page_class, page_class.resourceDirs, mix)
                
    def mixinResource(self, kls, resourceDirs, *path):        
        """TODO
        
        :param kls: TODO
        :param resourceDirs: TODO
        :param \*path: TODO"""
        path = os.path.join(*path)
        drive, path = os.path.splitdrive(path)
        if ':' in path:
            modName, clsName = path.split(':')
        else:
            modName, clsName = path, '*'
        modName = '%s%s'%(drive, modName)
        modPathList = self.getResourceList(resourceDirs, modName, 'py') or []
        if modPathList:
            modPathList.reverse()
            for modPath in modPathList:
                classMixin(kls, '%s:%s' % (modPath, clsName), only_callables=False, site=self)
        else:
            raise GnrMixinNotFound('Not found component %s' % modName)
            
    def py_requires_iterator(self, source_class, target_class):
        """TODO
        
        :param source_class: TODO
        :param target_class: TODO"""
        resourceDirs = target_class.resourceDirs
        py_requires = [x for x in splitAndStrip(getattr(source_class, 'py_requires', ''), ',') if x] or []
        for path in py_requires:
            drive, path = os.path.splitdrive(path)
            if ':' in path:
                modName, clsName = path.split(':')
            else:
                modName, clsName = path, '*'
            modName = '%s%s'%(drive, modName)
            modPathList = self.getResourceList(resourceDirs, modName, 'py') or []
            if modPathList:
                modPathList.reverse()
                for modPath in modPathList:
                    yield '%s:%s' % (modPath, clsName)
                    #classMixin(kls,'%s:%s'%(modPath,clsName),only_callables=False,site=self)
            else:
                raise GnrMixinError('Cannot import component %s' % modName)
                
    def getResourceList(self, resourceDirs, path, ext=None,pkg=None):
        """Find a resource in the current ``_resources`` folder or in parent folders one
        
        :param resourceDirs: TODO
        :param path: TODO
        :param ext: TODO"""
        result = []
        if ext == 'css' or ext == 'js':
            locations = resourceDirs[:]
            locations.reverse()
        else:
            locations = resourceDirs
        if ext and not path.endswith('.%s' % ext): path = '%s.%s' % (path, ext)
        if '*' in path:
            searchpath=os.path.split(path.split('*')[0])[0]
            use_glob=True
        else:
            searchpath=path
            use_glob=False
        for dpath in locations:
            fpath = os.path.join(dpath, searchpath)
            if os.path.exists(fpath):
                if use_glob:
                    result.extend(glob.glob(os.path.join(dpath,path)))
                else:
                    result.append(fpath)
        return uniquify(result)
        
    def getResourceClass(self, *path, **kwargs):
        """TODO"""
        resource_class = cloneClass('CustomResource', BaseResource)
        pkg=kwargs.pop('pkg', None)
        page=kwargs.pop('page', None)
        pluginId=kwargs.pop('pluginId', None)
        pkgOnly=kwargs.pop('pkgOnly', False)
        if pkg:
            resourceDirs = self.package_resourceDirs(pkg)
            lookupDirs = self.package_resourceDirs(pkg, omitSiteResources=pkgOnly, pluginId=pluginId)
        else:
            resourceDirs = lookupDirs = page.resourceDirs
        resource_class.resourceDirs = resourceDirs
        self.mixinResource(resource_class, lookupDirs, *path)
        return resource_class

    def loadResource(self, *path, **kwargs):
        return self.getResourceClass(*path, **kwargs)()
                 
    def mixinPageComponent(self, page, *path,**kwargs):
        """This method is used to mixin a component to a :ref:`webpage` at any time
        
        :param page: the target :ref:`webpage`
        :param \* path: the path of the :ref:`component <components>`"""
        pkg=kwargs.pop('pkg', None)
        pkgOnly=kwargs.pop('pkgOnly', False)
        pluginId=kwargs.pop('pluginId', None)
        component=self.loadResource(*path, page=page, pkg=pkg, pkgOnly=pkgOnly, pluginId=pluginId)
        setattr(component,'__mixin_pkg', pkg)
        setattr(component, '__mixin_path' ,'/'.join(path))
        css_requires = getattr(component,'css_requires',[])
        js_requires = getattr(component,'js_requires',[])
        for css in css_requires:
            if css and css not in page.envelope_css_requires and css not in page.css_requires:
                page.envelope_css_requires[css] = page.getResourceUri(css,'css',add_mtime=True,pkg=pkg)
        for js in js_requires:
            if js and js not in page.envelope_js_requires and js not in page.js_requires:
                page.envelope_js_requires[js] = page.getResourceUri(js,'js',add_mtime=True,pkg=pkg)
        page.mixin(component,**kwargs)
        if not hasattr(page,'mixin_set'):
            page.mixin_set = set()
        page.mixin_set.add(((tuple(path),tuple(kwargs.items()))))
        
    def _loadTableScript_getclass(self,modPathList,class_name):
        modPathList.reverse()
        basePath = modPathList.pop(0)
        resource_module = gnrImport(basePath, avoidDup=True)
        resource_class = getattr(resource_module, class_name, None)
        for modPath in modPathList:
            resource_module = gnrImport(modPath, avoidDup=True)
            custom_resource_class = getattr(resource_module, class_name, None)
            if resource_class:
                resource_class = clonedClassMixin(resource_class,custom_resource_class,only_callables=False)
        resource_class.py_extends = getattr(resource_class,'py_extends',None)
        return resource_class


    def loadTableScript(self, page, table=None, respath=None, class_name=None):
        resource_class,resource_table = self._loadTableScript_class(page,table=table,respath=respath,class_name=None)
        resource_obj = resource_class(page=page, resource_table=resource_table)
        return resource_obj

    def _loadTableScript_class(self, page, table=None, respath=None, class_name=None,ignoreCust=None):
        """TODO
        
        :param page: TODO
        :param table: the :ref:`database table <table>` name on which the query will be executed,
                      in the form ``packageName.tableName`` (packageName is the name of the
                      :ref:`package <packages>` to which the table belongs to)
        :param respath: TODO
        :param class_name: TODO
        """
        
        class_name = class_name or 'Main'
        application = self.gnrapp
        if ':' in respath:
            table, respath = respath.split(':')
        if isinstance(table, basestring):
            table = application.db.table(table)
        if not table:
            modPathList = self.getResourceList(page.resourceDirs, os.path.join('tables', '_default', *(respath.split('/'))), 'py') or []
            if modPathList:
                resource_class = self._loadTableScript_getclass(modPathList,class_name)
                return resource_class,None
            else:
                raise GnrWebServerError('Cannot import component %s' % respath)
        tablename = table.name
        pkgname = table.pkg.name
        table_modPathList = self.getResourceList(self.package_resourceDirs(table.pkg.name), 
                                                        os.path.join('tables', tablename, *(respath.split('/'))), 'py')
        if not table_modPathList:
            table_modPathList = self.getResourceList(page.resourceDirs, 
                                                            os.path.join('tables',  '_default', *(respath.split('/'))), 'py')
        custpkg_modPathList = None
        if not ignoreCust:
            custpkg_modPathList = self.getResourceList(page.resourceDirs, 
                                                   os.path.join('tables','_packages',pkgname, tablename, *(respath.split('/'))),'py')
        if custpkg_modPathList:
            resource_class = self._loadTableScript_getclass(custpkg_modPathList,class_name)
        elif table_modPathList:
            resource_class =  self._loadTableScript_getclass(table_modPathList,class_name)
        else:
            raise GnrWebServerError('Cannot import component %s %s' % respath,table.fullname)
        py_extends = resource_class.py_extends
        if py_extends =='*':
            py_extends = respath
            ignoreCust = True
        if py_extends: 
            parent_class,table = self._loadTableScript_class(page,table=table,respath=py_extends,class_name=class_name,
                                                            ignoreCust=ignoreCust)
            
            resource_class = clonedClassMixin(parent_class,resource_class,
                                            exclude='py_extends',only_callables=False)
        
        resource_class._gnrPublicName = '_tblscript.%s.%s.%s.%s' %(pkgname,tablename,respath,class_name)
        return resource_class,table
            
    
    def resourcesAtPath(self,page=None, pkg=None, path=None, ext='py'):
        """TODO
        
        :param pkg: the :ref:`package <packages>` object
        :param path: TODO
        :param ext: TODO"""
        result = Bag()
        if pkg:
            locations = list(self.package_resourceDirs(pkg,omitSiteResources=True))
        else:
            locations = page.resourceDirs
        for dpath in locations:
            dirpath = os.path.join(dpath, path)
            if os.path.isdir(dirpath):
                b = DirectoryResolver(dirpath, include='*.py', dropext=True)
                result.update(b, resolved=True)
        return result
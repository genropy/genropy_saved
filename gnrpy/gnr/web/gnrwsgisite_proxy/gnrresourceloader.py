#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  gnrresourceloader.py
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.

from gnr.core.gnrbag import Bag, DirectoryResolver
import os
from gnr.core.gnrlang import gnrImport, classMixin, cloneClass
from gnr.core.gnrstring import splitAndStrip
from gnr.core.gnrsys import expandpath
import inspect
from gnr.web.gnrwebpage import GnrWebPage
from gnr.web._gnrbasewebpage import GnrWebServerError
from gnr.web.gnrbaseclasses import BaseResource
from gnr.web.gnrbaseclasses import BaseWebtool
from gnr.core.gnrclasses import GnrMixinError
from gnr.core.gnrlang import uniquify
import glob
import logging

log = logging.getLogger(__name__)

class ResourceLoader(object):
    """Base class to load :ref:`intro_resources`"""
    def __init__(self, site=None):
        self.site = site
        self.site_path = self.site.site_path
        self.site_name = self.site.site_name
        self.gnr_config = self.site.gnr_config
        self.gnrapp = self.site.gnrapp
        self.debug = self.site.debug
        self.gnr_static_handler = self.site.getStatic('gnr')
        self.build_automap()
        self.page_factories = {}
        self.default_path = self.site.default_page and self.site.default_page.split('/')
        
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
        
    def build_automap(self):
        """Build the :ref:`automap` file"""
        def handleNode(node, pkg=None, plugin=None):
            attr = node.attr
            file_name = attr['file_name']
            node.attr = dict(
                    name='!!%s' % file_name.capitalize(),
                    pkg=pkg
                    )
            if plugin:
                node.attr['plugin']=plugin
            if attr['file_ext'] == 'py':
                node.attr['path'] = attr['rel_path']
            node.label = file_name
            if node._value is None:
                node._value = ''
                
        self.automap = DirectoryResolver(os.path.join(self.site_path, 'pages'), ext='py', include='*.py',
                                         exclude='_*,.*,*.pyc')()
                                         
        self.automap.walk(handleNode, _mode='', pkg='*')
        for package in self.site.gnrapp.packages.values():
            packagemap = DirectoryResolver(os.path.join(package.packageFolder, 'webpages'),
                                           include='*.py', exclude='_*,.*')()
            packagemap.walk(handleNode, _mode='', pkg=package.id)
            self.automap.setItem(package.id, packagemap, name=package.attributes.get('name_long') or package.id)
            for pluginname,plugin in package.plugins.items():
                pluginmap = DirectoryResolver(plugin.webpages_path,
                                               include='*.py', exclude='_*,.*')()
                pluginmap.walk(handleNode, _mode='', pkg=package.id,plugin=plugin.id)
                self.automap.setItem("%s._plugin.%s"%(package.id,plugin.id), pluginmap, name=plugin.id)
        self.automap.toXml(os.path.join(self.site_path, 'automap.xml'))
        
    @property
    def sitemap(self):
        """Return the sitemap Bag (if there is no sitemap, creates it)"""
        if not hasattr(self, '_sitemap'):
            sitemap_path = os.path.join(self.site_path, 'sitemap.xml')
            if not os.path.isfile(sitemap_path):
                sitemap_path = os.path.join(self.site_path, 'automap.xml')
            _sitemap = Bag(sitemap_path)
            _sitemap.setBackRef()
            self._sitemap = _sitemap
        return self._sitemap
        
    def get_page_node(self, path_list, default_path=None):
        """Get the deepest :ref:`bagnode` in the sitemap :ref:`bag` associated with the given url
        
        :param path_list: TODO
        :param default: TODO"""
        def escape_path_list(path_list):
            return [p.replace('.','\\.') for p in path_list]
        def unescape_path_list(path_list):
            return [p.replace('\\.','.') for p in path_list]
        path_list = escape_path_list(path_list)
        page_node = self.sitemap.getDeepestNode('.'.join(path_list))
        if not page_node and self.site.mainpackage: # try in the main package
            page_node = self.sitemap.getDeepestNode('.'.join([self.site.mainpackage] + path_list))
        if page_node:
            page_node_attributes = page_node.getInheritedAttributes()
            if page_node_attributes.get('path'):
                page_node._tail_list=unescape_path_list(getattr(page_node,'_tail_list',[]))
                return page_node, page_node_attributes
            else:
                page_node = self.sitemap.getDeepestNode('.'.join(path_list + ['index']))
                if page_node:
                    page_node_attributes = page_node.getInheritedAttributes()
                    if page_node_attributes.get('path'):
                        page_node._tail_list=unescape_path_list(getattr(page_node,'_tail_list',[]))
                        return page_node, page_node_attributes
        if not page_node and default_path:
            page_node, page_node_attributes = self.get_page_node(default_path)
            if page_node:
                page_node._tail_list =  unescape_path_list(path_list)
            return page_node, page_node_attributes
        return None, None
        
    def __call__(self, path_list, request, response, environ=None,request_kwargs=None):
        page_node = None
        request_kwargs = request_kwargs or dict()
        mobile = request_kwargs.pop('_mobile',False)
        if mobile:
            page_node, page_node_attributes = self.get_page_node(['mobile']+path_list)
        if not page_node:
            page_node, page_node_attributes = self.get_page_node(path_list, default_path=self.default_path)
        if not page_node:
            return None
        request_args = page_node._tail_list
        path = page_node_attributes.get('path')
        pkg = page_node_attributes.get('pkg')
        plugin = page_node_attributes.get('plugin')
        page_class = self.get_page_class(path=path, pkg=pkg, plugin=plugin,request_args=request_args,request_kwargs=request_kwargs)
        page = page_class(site=self.site, request=request, response=response,
                          request_kwargs=request_kwargs, request_args=request_args,
                          filepath=path, packageId=page_class._packageId, pluginId=plugin,  basename=path, environ=environ)
        return page
        
    def get_page_class(self, path=None, pkg=None, plugin=None,request_args=None,request_kwargs=None):
        """TODO
        
        :param path: TODO
        :param pkg: the :ref:`package <packages>` object"""
        if pkg == '*':
            module_path = os.path.join(self.site_path, path)
            pkg = self.site.config['packages?default']
        else:
            if plugin:
                module_path= os.path.join(self.gnrapp.packages[pkg].plugins[plugin].webpages_path, path)
            else:
                module_path = os.path.join(self.gnrapp.packages[pkg].packageFolder, 'webpages', path)
            
        # if module_path in self.page_factories:
        #    return self.page_factories[module_path]
        page_module = gnrImport(module_path, avoidDup=True)
        page_factory = getattr(page_module, 'page_factory', GnrWebPage)
        custom_class = getattr(page_module, 'GnrCustomWebPage')
        mainPkg = pkg
        if hasattr(custom_class,'getMainPackage'):
            kw = dict()
            if 'page_id' in request_kwargs:
                kw = self.site.register.pageStore(request_kwargs['page_id']).getItem('pageArgs') or dict()
                kw.update(request_kwargs)
            mainPkg = custom_class.getMainPackage(request_args=request_args,request_kwargs=kw)
        py_requires = splitAndStrip(getattr(custom_class, 'py_requires', ''), ',')
        plugin_webpage_classes = self.plugin_webpage_classes(path, pkg=mainPkg)
        for plugin_webpage_class in plugin_webpage_classes:
            plugin_py_requires = splitAndStrip(getattr(plugin_webpage_class, 'py_requires', ''), ',')
            py_requires.extend(plugin_py_requires)
        page_class = cloneClass('GnrCustomWebPage', page_factory)
        page_class.__module__ = page_module.__name__
        self.page_class_base_mixin(page_class, pkg=mainPkg)
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
        page_class.pageOptions = getattr(custom_class, 'pageOptions', {})
        page_class.auth_tags = getattr(custom_class, 'auth_tags', '')
        page_class.resourceDirs = self.page_class_resourceDirs(page_class, module_path, pkg=mainPkg)
        self.page_pyrequires_mixin(page_class, py_requires)
        classMixin(page_class, custom_class, only_callables=False)
        page_class.css_requires.extend([x for x in splitAndStrip(getattr(custom_class, 'css_requires', ''), ',') if x])
        page_class.tpldirectories = page_class.resourceDirs + [
                self.gnr_static_handler.path(page_class.gnrjsversion, 'tpl')]
        page_class._packageId = mainPkg
        self.page_class_plugin_mixin(page_class, plugin_webpage_classes)
        self.page_class_custom_mixin(page_class, path, pkg=mainPkg)
        self.page_factories[module_path] = page_class
        return page_class
        
    def page_class_base_mixin(self, page_class, pkg=None):
        """Look for custom classes in the package
        
        :param page_class: TODO
        :param pkg: the :ref:`package <packages>` object"""
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
            pagesPath = os.path.join(self.gnrapp.packages[pkg].packageFolder, 'webpages')
            packageResourcePath =  os.path.join(self.gnrapp.packages[pkg].packageFolder, 'resources')
        else:
            pagesPath = os.path.join(self.site_path, 'pages')
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
            pagesPath = os.path.join(pkg.packageFolder, 'webpages')
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
            fpath = os.path.join(pagesPath, '_resources')
            if os.path.isdir(fpath):
                pkgResourceDirs.append(fpath) # we add a resource folder for common package
            rsrc_path = os.path.join(pkg.packageFolder, 'resources')
            if os.path.isdir(rsrc_path):
                pkgResourceDirs.append(rsrc_path)
            pkg._siteResourceDirs = self.site.resources_dirs
            pkg._resourceDirs = pkgResourceDirs
        if pluginId and pluginId in pkg.plugins:
            plugin = pkg.plugins[pluginId]
            if plugin.resources_path:
                result.append(plugin.resources_path)
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
        if ':' in path:
            modName, clsName = path.split(':')
        else:
            modName, clsName = path, '*'
        modPathList = self.getResourceList(resourceDirs, modName, 'py') or []
        if modPathList:
            modPathList.reverse()
            for modPath in modPathList:
                classMixin(kls, '%s:%s' % (modPath, clsName), only_callables=False, site=self)
        else:
            raise GnrMixinError('Cannot import component %s' % modName)
            
    def py_requires_iterator(self, source_class, target_class):
        """TODO
        
        :param source_class: TODO
        :param target_class: TODO"""
        resourceDirs = target_class.resourceDirs
        py_requires = [x for x in splitAndStrip(getattr(source_class, 'py_requires', ''), ',') if x] or []
        for path in py_requires:
            if ':' in path:
                modName, clsName = path.split(':')
            else:
                modName, clsName = path, '*'
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
        
    def loadResource(self, *path, **kwargs):
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
        return resource_class()
                 
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
            if css and not css in page.dynamic_css_requires and not css in page.css_requires:
                page.dynamic_css_requires[css] = page.getResourceUri(css,'css',add_mtime=True,pkg=pkg)
        for js in js_requires:
            if js and not js in page.dynamic_js_requires and not js in page.js_requires:
                page.dynamic_js_requires[js] = page.getResourceUri(js,'js',add_mtime=True,pkg=pkg)
        page.mixin(component,**kwargs)
    
        
    def loadTableScript(self, page, table=None, respath=None, class_name=None):
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
            tablename = '_default'
            modName = os.path.join('tables', tablename, *(respath.split('/')))
        else:
            tablename = table.name
            pkgname = table.pkg.name
            modName = os.path.join('tables','_packages',pkgname, tablename, *(respath.split('/')))
        resourceDirs = page.resourceDirs
        modPathList = self.getResourceList(resourceDirs, modName, 'py')
        if not modPathList and table is not None:
            resourceDirs = self.package_resourceDirs(table.pkg.name)
            modName = os.path.join('tables', tablename, *(respath.split('/')))
            modPathList = self.getResourceList(resourceDirs, modName, 'py')
            if not modPathList:
                tablename = '_default'
                resourceDirs = page.resourceDirs
                modName = os.path.join('tables', tablename, *(respath.split('/')))
                modPathList = self.getResourceList(resourceDirs, modName, 'py')
        modPathList = self.getResourceList(resourceDirs, modName, 'py') or []
        if modPathList:
            modPathList.reverse()
            basePath = modPathList.pop(0)
            resource_module = gnrImport(basePath, avoidDup=True)
            resource_class = getattr(resource_module, class_name, None)
            for modPath in modPathList:
                resource_module = gnrImport(modPath, avoidDup=True)
                resource_class =cloneClass('CustomResource', resource_class)
                custom_resource_class = getattr(resource_module, class_name, None)
                if resource_class:
                    classMixin(resource_class, custom_resource_class, only_callables=False)
            resource_obj = resource_class(page=page, resource_table=table)
            return resource_obj
        else:
            raise GnrWebServerError('Cannot import component %s' % modName)
    
    def resourcesAtPath(self,page=None, pkg=None, path=None, ext='py'):
        """TODO
        
        :param pkg: the :ref:`package <packages>` object
        :param path: TODO
        :param ext: TODO"""
        result = Bag()
        if pkg:
            locations = list(self.package_resourceDirs(pkg))
        else:
            locations = page.resourceDirs
        for dpath in locations:
            dirpath = os.path.join(dpath, path)
            if os.path.isdir(dirpath):
                b = DirectoryResolver(dirpath, include='*.py', dropext=True)
                result.update(b, resolved=True)
        return result
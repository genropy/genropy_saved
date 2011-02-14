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
from gnr.core.gnrlang import gnrImport, classMixin, cloneClass, instanceMixin
from gnr.core.gnrstring import splitAndStrip
from gnr.core.gnrsys import expandpath
import inspect
from gnr.web.gnrwebpage import GnrWebPage
from gnr.web._gnrbasewebpage import GnrWebServerError
from gnr.web.gnrbaseclasses import BaseResource
from gnr.web.gnrbaseclasses import BaseWebtool
import glob
import logging

log = logging.getLogger(__name__)

class GnrMixinError(Exception):
    pass

class ResourceLoader(object):
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
        def handleNode(node, pkg=None):
            attr = node.attr
            file_name = attr['file_name']
            node.attr = dict(
                    name='!!%s' % file_name.capitalize(),
                    pkg=pkg
                    )
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
        self.automap.toXml(os.path.join(self.site_path, 'automap.xml'))

    @property
    def sitemap(self):
        if not hasattr(self, '_sitemap'):
            sitemap_path = os.path.join(self.site_path, 'sitemap.xml')
            if not os.path.isfile(sitemap_path):
                sitemap_path = os.path.join(self.site_path, 'automap.xml')
            _sitemap = Bag(sitemap_path)
            _sitemap.setBackRef()
            self._sitemap = _sitemap
        return self._sitemap

    def get_page_node(self, path_list, default=False):
        # get the deepest node in the sitemap bag associated with the given url
        page_node = self.sitemap.getDeepestNode('.'.join(path_list))
        if not page_node and self.site.mainpackage: # try in the main package
            page_node = self.sitemap.getDeepestNode('.'.join([self.site.mainpackage] + path_list))
        if page_node:
            page_node_attributes = page_node.getInheritedAttributes()
            if page_node_attributes.get('path'):
                return page_node, page_node_attributes
            else:
                page_node = self.sitemap.getDeepestNode('.'.join(path_list + ['index']))
                if page_node:
                    page_node_attributes = page_node.getInheritedAttributes()
                    if page_node_attributes.get('path'):
                        return page_node, page_node_attributes
        if self.default_path and not default:
            page_node, page_node_attributes = self.get_page_node(self.default_path, default=True)
            page_node._tail_list = list(path_list)
            return page_node, page_node_attributes
        return None, None


    def __call__(self, path_list, request, response, environ=None):
        page_node, page_node_attributes = self.get_page_node(path_list)
        if not page_node:
            return None
        request_args = page_node._tail_list
        path = page_node_attributes.get('path')
        pkg = page_node_attributes.get('pkg')
        page_class = self.get_page_class(path=path, pkg=pkg)
        page = page_class(site=self.site, request=request, response=response,
                          request_kwargs=self.site.parse_request_params(request.params), request_args=request_args,
                          filepath=path, packageId=pkg, basename=path, environ=environ)
        return page

    def get_page_class(self, path=None, pkg=None):
        if pkg == '*':
            module_path = os.path.join(self.site_path, path)
            pkg = self.site.config['packages?default']
        else:
            module_path = os.path.join(self.gnrapp.packages[pkg].packageFolder, 'webpages', path)

        # if module_path in self.page_factories:
        #    return self.page_factories[module_path]
        page_module = gnrImport(module_path, avoidDup=True)
        page_factory = getattr(page_module, 'page_factory', GnrWebPage)
        custom_class = getattr(page_module, 'GnrCustomWebPage')
        py_requires = splitAndStrip(getattr(custom_class, 'py_requires', ''), ',')
        plugin_webpage_classes = self.plugin_webpage_classes(path, pkg=pkg)
        for plugin_webpage_class in plugin_webpage_classes:
            plugin_py_requires = splitAndStrip(getattr(plugin_webpage_class, 'py_requires', ''), ',')
            py_requires.extend(plugin_py_requires)
        page_class = cloneClass('GnrCustomWebPage', page_factory)
        page_class.__module__ = page_module
        self.page_class_base_mixin(page_class, pkg=pkg)
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
        page_class.eagers = getattr(custom_class, 'eagers', {})
        page_class.css_requires = []
        page_class.js_requires = splitAndStrip(getattr(custom_class, 'js_requires', ''), ',')
        page_class.pageOptions = getattr(custom_class, 'pageOptions', {})
        page_class.auth_tags = getattr(custom_class, 'auth_tags', '')
        page_class.resourceDirs = self.page_class_resourceDirs(page_class, module_path, pkg=pkg)
        self.page_pyrequires_mixin(page_class, py_requires)
        classMixin(page_class, custom_class, only_callables=False)
        page_class.css_requires.extend([x for x in splitAndStrip(getattr(custom_class, 'css_requires', ''), ',') if x])
        page_class.tpldirectories = page_class.resourceDirs + [
                self.gnr_static_handler.path(page_class.gnrjsversion, 'tpl')]
        page_class._packageId = pkg
        self.page_class_plugin_mixin(page_class, plugin_webpage_classes)
        self.page_class_custom_mixin(page_class, path, pkg=pkg)
        self.page_factories[module_path] = page_class
        return page_class

    def page_class_base_mixin(self, page_class, pkg=None):
        """Looks for custom classes in the package"""
        if pkg:
            package = self.gnrapp.packages[pkg]
        if package and package.webPageMixin:
            classMixin(page_class, package.webPageMixin, only_callables=False) # first the package standard
        if self.gnrapp.webPageCustom:
            classMixin(page_class, self.gnrapp.webPageCustom, only_callables=False) # then the application custom
        if package and package.webPageMixinCustom:
            classMixin(page_class, package.webPageMixinCustom, only_callables=False) # finally the package custom

    def plugin_webpage_classes(self, path, pkg=None):
        """Look in the plugins folders for a file named as the current webpage and get all classes"""
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
        """Mixin the current class with  plugin_webpage_classes"""
        for plugin_webpage_class in plugin_webpage_classes:
            classMixin(page_class, plugin_webpage_class, only_callables=False)

    def page_class_custom_mixin(self, page_class, path, pkg=None):
        """Look in the instance custom folder for a file named as the current webpage"""
        path = path.split(os.path.sep)
        if pkg:
            customPagePath = os.path.join(self.gnrapp.customFolder, pkg, 'webpages', *path)
            if os.path.isfile(customPagePath):
                component_page_module = gnrImport(customPagePath, avoidDup=True)
                component_page_class = getattr(component_page_module, 'WebPage', None)
                if component_page_class:
                    classMixin(page_class, component_page_class, only_callables=False)

    def page_class_resourceDirs(self, page_class, path, pkg=None):
        """Build page resources dirs"""
        if pkg:
            pagesPath = os.path.join(self.gnrapp.packages[pkg].packageFolder, 'webpages')
        else:
            pagesPath = os.path.join(self.site_path, 'pages')
        curdir = os.path.dirname(os.path.join(pagesPath, path))
        resourcePkg = None
        result = [] # result is now empty
        if pkg: # for index page or other pages at root level (out of any package)
            resourcePkg = self.gnrapp.packages[pkg].attributes.get('resourcePkg')
            fpath = os.path.join(self.site_path, '_custom', pkg, '_resources')
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
                fpath = os.path.join(self.gnrapp.packages[rp].packageFolder, 'webpages', '_resources')
                if os.path.isdir(fpath):
                    result.append(fpath)
            #result.extend(self.siteResources)
        resources_list = self.site.resources_dirs
        result.extend(resources_list)
        return result

    def package_resourceDirs(self, pkg):
        pkg = self.gnrapp.packages[pkg]
        if not hasattr(pkg, '_resourceDirs'):
            pagesPath = os.path.join(pkg.packageFolder, 'webpages')
            resourcePkg = None
            result = [] # result is now empty
            resourcePkg = pkg.attributes.get('resourcePkg')
            fpath = os.path.join(self.site_path, '_custom', pkg.id, '_resources')
            if os.path.isdir(fpath):
                result.append(fpath) # we add a custom resource folder for current package

            if resourcePkg:
                for rp in resourcePkg.split(','):
                    fpath = os.path.join(self.site_path, '_custom', pkg.id, '_resources')
                    if os.path.isdir(fpath):
                        result.append(fpath)
            fpath = os.path.join(pagesPath, '_resources')
            if os.path.isdir(fpath):
                result.append(fpath) # we add a resource folder for common package
            result.extend(self.site.resources_dirs)
            pkg._resourceDirs = result
            # so we return a list of any possible resource folder starting from
        # most customized and ending with most generic ones
        return pkg._resourceDirs


    def site_resources(self):
        resources = Bag()
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
        return resources

    def resource_name_to_path(self, res_id, safe=True):
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
        for mix in py_requires:
            if mix:
                self.mixinResource(page_class, page_class.resourceDirs, mix)


    def mixinResource(self, kls, resourceDirs, *path):
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

    def getResourceList(self, resourceDirs, path, ext=None):
        """Find a resource in current _resources folder or in parent folders one"""
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
        return result

    def loadResource(self, pkg, *path):
        resourceDirs = self.package_resourceDirs(pkg)
        resource_class = cloneClass('CustomResource', BaseResource)
        resource_class.resourceDirs = resourceDirs
        self.mixinResource(resource_class, resourceDirs, *path)
        return resource_class()

    def loadTableScript(self, page, table=None, respath=None, class_name=None, _onDefault=None):
        class_name = class_name or 'Main'
        application = self.gnrapp
        if not table:
            _onDefault = True
        if ':' in respath:
            table, respath = respath.split(':')
        if _onDefault:
            tablename = '_default'
            resourceDirs = page.resourceDirs
        else:
            if isinstance(table, basestring):
                table = application.db.table(table)
            tablename = table.name
            resourceDirs = self.package_resourceDirs(table.pkg.name)
        modName = os.path.join('tables', tablename, *(respath.split('/')))
        #resourceDirs = application.packages[table.pkg.name].resourceDirs
        modPathList = self.getResourceList(resourceDirs, modName, 'py') or []
        if modPathList:
            modPathList.reverse()
            basePath = modPathList.pop(0)
            resource_module = gnrImport(basePath, avoidDup=True)
            resource_class = getattr(resource_module, class_name, None)
            resource_obj = resource_class(page=page, resource_table=table)
            for modPath in modPathList:
                resource_module = gnrImport(modPath, avoidDup=True)
                resource_class = getattr(resource_module, class_name, None)
                if resource_class:
                    instanceMixin(resource_obj, resource_class, only_callables=False)
            return resource_obj
        elif not _onDefault:
            return self.loadTableScript(page, table=table, respath=respath, _onDefault=True)
        else:
            raise GnrWebServerError('Cannot import component %s' % modName)


    def resourcesAtPath(self, pkg, path, ext):
        result = Bag()
        locations = list(self.package_resourceDirs(pkg))
        for dpath in locations:
            dirpath = os.path.join(dpath, path)
            if os.path.isdir(dirpath):
                b = DirectoryResolver(dirpath, include='*.py', dropext=True)
                result.update(b, resolved=True)
        return result

        

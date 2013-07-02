# -*- coding: UTF-8 -*-
from gnr.core.gnrbag import Bag
import inspect
import os
import sys
from gnr.core.gnrbaseservice import GnrBaseService
from gnr.core.gnrlang import  gnrImport
import logging

log = logging.getLogger(__name__)



def is_ServiceHandler(cls, service_names=None):
    service_name_find= lambda kls: getattr(kls,'service_name', kls.__name__.lower())
    cls_compatible = lambda kls: inspect.isclass(kls) and issubclass(kls, GnrBaseService) and kls is not GnrBaseService
    name_compatible = lambda kls: service_name_find(kls) in service_names if service_names else True
    return cls_compatible(cls) and name_compatible(cls)

class ServiceHandlerManager(object):
    """ This class handles the StaticHandlers"""

    def __init__(self, site):
        self.site = site
        self.services = Bag()

    def addAllStatics(self, module=None):
        """inspect self (or other modules) for StaticHandler subclasses and
        do addStatic for each"""
        module = module or sys.modules[self.__module__]

        servicehandler_classes = inspect.getmembers(module, is_ServiceHandler)
        for servicehandler in servicehandler_classes:
            self.add(servicehandler[1])

    def service_name(self, service):
        return getattr(service,'service_name', service.__name__.lower())

    def addSiteServices(self):
        services = self.site.config['services']
        if not services:
            return
        for service in services:
            kw = dict(service.attr)
            resource = kw.pop('resource')
            service_type = kw.pop('service_type',service.label)
            resmodule,resclass = resource.split(':') if ':' in resource else resource,'Main'
            modules = self.site.resource_loader.getResourceList(self.site.resources_dirs, 'services/%s/%s.py' %(service_type,resmodule))
            assert modules,'Missing module %s for service %s '  %(resmodule,service_type)    
            module = modules[0]
            try:
                module = gnrImport(module)
                service_class = getattr(module,resclass)
                self.add(service_class,service_name=service.label,**kw)
            except ImportError, import_error:
                log.exception("Could not import %s"%module)
                log.exception(str(import_error))

    def addSiteServices_old(self, service_names=None):
        service_list = []
        if isinstance(service_names, basestring):
            service_names = service_names.replace(';',',').split(',')
        if service_names:
            service_finder = lambda cls: is_ServiceHandler(cls, service_names=service_names)
        elif service_names==[]:
            return
        else:
            service_finder = is_ServiceHandler
        modules = self.site.resource_loader.getResourceList(self.site.resources_dirs, 'services/*.py')
        for module_file in modules:
            try:
                module = gnrImport(module_file)
            except ImportError, import_error:
                log.exception("Could not import %s"%module_file)
                log.exception(str(import_error))
            else:
                service_list.extend(inspect.getmembers(module, service_finder))
        for service in service_list:
            service = service[1]
            service_name = self.service_name(service)
            service_kwargs = self.site.config.getAttr('services.%s' % service_name) or dict()
            self.add(service,service_name=service_name,**service_kwargs)


    def add(self, service_handler_factory, service_name=None, **kwargs):
        service_name = service_name or self.service_name(service_handler_factory)
        service_handler = service_handler_factory(self.site, **kwargs)
        self.services.setItem(service_name, service_handler, **kwargs)
        return service_handler

    def get(self, service_name):
        return self.services[service_name]

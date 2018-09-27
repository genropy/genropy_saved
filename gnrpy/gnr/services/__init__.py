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

#Created by Giovanni Porcari on 2007-03-24.
#Copyright (c) 2007 Softwell. All rights reserved.

import os

import logging

from collections import OrderedDict
from gnr.core.gnrlang import  gnrImport,clonedClassMixin

log = logging.getLogger(__name__)


PKGMARKER = '%spackages%s' %(os.sep,os.sep)

class ServiceHandler(object):

    def __init__(self,site):
        self.site = site
        resdirs = site.resource_loader.getResourceList(site.resources_dirs,'services')
        resdirs.reverse()
        self.service_types = {}
        base_service_type = GnrBaseServiceType
        for service_root in resdirs:
            service_types = os.listdir(service_root)
            for service_type in service_types:
                if not os.path.isdir(os.path.join(service_root,service_type)):
                    continue
                service_type_factory = base_service_type
                if PKGMARKER in service_root:
                    libtype = service_root.replace('resources','lib')
                    if os.path.isdir(libtype):
                        m = os.path.join(libtype,'%s.py' %service_type)
                        package_service_lib = os.path.join(libtype)
                        if os.path.exists(package_service_lib):
                            z = gnrImport(package_service_lib)
                            if hasattr(z,'BaseServiceType'):
                                base_service_type = z.BaseServiceType
                                service_type_factory = base_service_type
                        service_type_module = gnrImport(m)
                        service_type_factory = getattr(service_type_module,'ServiceType',None) or service_type_factory
                self.service_types[service_type] = service_type_factory(self.site,service_type=service_type)
    
    def getService(self,service_type=None,service_name=None):
        if not service_type in self.service_types:
            servattr = self.site.config.getAttr('services.%s' %service_type) #backward
            if servattr:
                service_type = servattr['service_type']
            else:
                return
        return self(service_type)(service_name)
    
    def __call__(self,service_type):
        return self.service_types[service_type]


class GnrBaseServiceType(object):
    def __init__(self, site=None,service_type=None):
        self.site = site
        self.service_type = service_type
        self.service_instances = {}


    def addService(self, service_name=None):
        service_conf = self.getConfiguration(service_name)
        instance = None
        implementation = None
        if service_conf:
            implementation = service_conf.pop('implementation',None) or service_conf.pop('resource',None) #resource is the oldname for implementation
        service_factory = self.getServiceFactory(implementation)
        if not service_factory:
            return
        service = service_factory(self.site,service_name=service_name,**service_conf)
        self.service_instances[service_name] = service
        return service

    def configurations(self):
        typeconf = self.site.config['services.%s' %self.service_type]
        if not typeconf:
            result = []
            for k,attr in self.site.config['services'].digest('#k,#a'):
                service_type = attr.pop('service_type',None) or k
                if service_type == self.service_type:
                    result.append(dict(service_name=k, service_type=service_type,**attr))
            return result
        return [dict(service_name=k,service_type=attr.pop('service_type',None),**attr) for attr in typeconf.digest('#a')]


    def getConfiguration(self,service_name):
        conf = self.site.config.getAttr('services.%s' %service_name)
        if not conf:
            conf = self.site.config.getAttr('services.%s.%s' %(self.service_type,service_name))
        return conf

    @property
    def implementations(self):
        if not hasattr(self,'_implementations'):
            self._implementations = {}
            dirs = self.site.resource_loader.getResourceList(self.site.resources_dirs, 'services/%s' %(self.service_type))
            self.baseImplementation = None
            for d in dirs:
                for impl in os.listdir(d):
                    impl = os.path.join(d,impl)
                    implname,implext = os.path.split(impl)
                    if os.path.isdir(impl):
                        impl = os.path.join(d,impl,'service.py')
                        if not os.path.exists(impl):
                            continue
                        implext = '.py'
                    if implext!='.py':
                        continue
                    try:
                        module = gnrImport(impl)
                        service_class = getattr(module,'Service',None) or getattr(module,'Main',None) #backward compatibility
                    except ImportError as imperr:
                        log.exception("Could not import %s"%module)
                        log.exception(str(imperr))
                    self._implementations[implname] =  service_class
                    if not self.baseImplementation:
                        self.baseImplementation = service_class

        return self._implementations

    def getServiceFactory(self,implementation):
        return self.implementations.get(implementation) or self.baseImplementation

    def __call__(self, service_name=None):
        service = self.service_instances.get(service_name)
        if service is None:
            service = self.addService(service_name)            
        return service
        

class GnrBaseService(object):
    def __init__(self, parent):
        self.parent = parent


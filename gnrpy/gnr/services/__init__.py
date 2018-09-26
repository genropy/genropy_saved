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
from gnr.core.gnrlang import  gnrImport,clonedClassMixin

PKGMARKER = '%spackages%s' %(os.sep,os.sep)

class GnrBaseServiceType(object):
    def __init__(self, site):
        self.site = site
        self.instances = {}

    def add(self, service_name=None):
        instance_config = self.getConfiguration(service_name)
        self.instances[service_name] = instance
        #service_name = service_name or self.service_name(service_handler_factory)
        #service_handler = service_handler_factory(self.site, **kwargs)
        #service_handler.service_name = service_name
        #self.services.setItem(service_name, service_handler, **kwargs)
        #return service_handler

    def getConfiguration(self,service_name):
        conf = self.site.config.getAttr('services.%s' %service_name)


    def get(self, service_type=None,service_name=None):
        service = self.services[service_name]
        if service is None:
            if ':' in service_name:
                service_name, resource = service_name.split(':')
            else:
                resource = service_name
            service_handler_factory = self.importServiceClass(service_type=service_name,resource=resource)
            if service_handler_factory:
                service = self.add(service_handler_factory,service_name=service_name)
        return service
        
class ServiceHandler(object):
    default_service_type_factory = GnrBaseServiceType

    def __init__(self,site):
        self.site = site
        resdirs = site.resource_loader.getResourceList(site.resources_dirs,'services')
        resdirs.reverse()
        self.services = {}
        sep = os.sep
        for service_root in resdirs:
            service_types = os.listdir(service_root)
            for service_type in service_types:
                if not os.path.isdir(service_root,service_type):
                    continue
                service_type_factory = self.default_service_type_factory
                if PKGMARKER in service_root:
                    libtype = os.path.join(service_root,'..','..','lib','services',service_type)
                    if os.path.isdir(libtype):
                        service_type_module = gnrImport(libtype,'__init__')
                        service_type_factory = getattr(service_type_module,'ServiceType')
                self.services[service_type] = service_type_factory(self.site)


class GnrBaseService(object):
    def __init__(self, parent):
        self.parent = parent


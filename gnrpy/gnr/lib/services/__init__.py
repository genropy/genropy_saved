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

from builtins import map
from builtins import str
#from builtins import object
import os

import sys

from collections import OrderedDict
from gnr.core.gnrlang import  gnrImport,clonedClassMixin
from datetime import datetime
from gnr.core.gnrbag import Bag

import logging
log = logging.getLogger(__name__)


PKGMARKER = '%spackages%s' %(os.sep,os.sep)

LIB_ROOT = os.path.dirname(__file__)

class ServiceHandler(object):

    
    def __init__(self,site):
        self.site = site
        #cerco definizioni core
        service_types_classes = []
        service_types_factories = {}
        self.service_types = {}
        services_roots = [LIB_ROOT]
        for pkg,pkgobj in list(self.site.gnrapp.packages.items()):
            pkglibroot = os.path.join(pkgobj.packageFolder,'lib','services')
            if os.path.isdir(pkglibroot):
                services_roots.append(pkglibroot)
        default_service_type_factory = BaseServiceType
        all_service_types = set()
        for service_root in services_roots:
            service_types = [service_type for service_type, ext in map(os.path.splitext, os.listdir(service_root)) if ext=='.py']
            for service_type in service_types:
                if service_type=='__init__': continue
                all_service_types.add(service_type)
                m = gnrImport(os.path.join(service_root,'%s.py' %service_type))
                service_type_factory = getattr(m,'ServiceType',None)
                if service_type_factory:
                    service_types_factories[service_type] = service_type_factory
        resdirs = site.resource_loader.getResourceList(site.resources_dirs,'services')
        resdirs.reverse()
        for service_root in resdirs:
            for service_type in list(all_service_types):
                if not os.path.isdir(os.path.join(service_root,service_type)):
                    continue
                service_type_factory = service_types_factories.get(service_type) or default_service_type_factory
                self.service_types[service_type] = service_type_factory(self.site,service_type=service_type)
        
    def getService(self,service_type=None,service_name=None, **kwargs):
        
        if service_type not in self.service_types:
            self.service_types[service_type] = BaseServiceType(site=self.site,service_type=service_type)
        return self(service_type)(service_name, **kwargs)
    
    def __call__(self,service_type):
        return self.service_types[service_type]


class BaseServiceType(object):
    
    def __init__(self, site=None,service_type=None, **kwargs):
        self.site = site
        self.service_type = service_type
        self.service_instances = {}        

    def addService(self, service_name=None, **kwargs):
        service_conf = kwargs or self.getConfiguration(service_name)
        implementation = None
        if service_conf:
            implementation = service_conf.pop('implementation',None) or service_conf.pop('resource',None) #resource is the oldname for implementation
        service_factory = self.getServiceFactory(implementation)
        if not service_factory:
            return
        service_conf = service_conf or {}
        service = service_factory(self.site,**service_conf)
        service.service_name = service_name
        service.service_implementation = implementation
        self.service_instances[service_name] = service
        return service

    def getConfiguration(self,service_name):
        return self.getServiceConfigurationFromDb(service_name) or \
                self.getServiceConfigurationFromSiteConfig(service_name) or \
                self.getServiceConfigurationFromSelf(service_name)
       
    
    def configurations(self):
        l = self.serviceConfigurationsFromSiteConfig()
        if 'sys' in list(self.site.gnrapp.packages.keys()):
            dbservices = self.site.db.table('sys.service').query(where='$service_type=:st',st=self.service_type).fetch()
            l += [dict(implementation=r['implementation'],service_name=r['service_name'],service_type=r['service_type']) for r in dbservices]
        return l


    def getServiceConfigurationFromDb(self,service_name):
        if 'sys' in list(self.site.gnrapp.packages.keys()):
            service_record = self.site.db.table('sys.service').record(service_type=self.service_type,
                                                            service_name=service_name,ignoreMissing=True).output('dict')
            if not service_record:
                return
            conf =  Bag(service_record['parameters'])
            conf['implementation'] = service_record['implementation']
            return conf.asDict()
   
        
    def getServiceConfigurationFromSelf(self,service_name):
        handler = getattr(self,'conf_%s' %service_name,None)
        return handler() if handler else None

    def serviceConfigurationsFromSiteConfig(self):
        if not self.site.config['services']:
            return []
        typeconf = self.site.config['services.%s' %self.service_type]
        if not typeconf:
            result = []
            for k,attr in self.site.config['services'].digest('#k,#a'):
                attr = dict(attr)
                service_type = attr.pop('service_type',None) or k
                if service_type == self.service_type:
                    result.append(dict(service_name=k, service_type=service_type,**attr))
            return result
        return [dict(service_name=k,service_type=attr.pop('service_type',None),**attr) for attr in typeconf.digest('#a')]

    def getServiceConfigurationFromSiteConfig(self,service_name):
        conf = self.site.config.getAttr('services.%s' %service_name)
        if not conf:
            conf = self.site.config.getAttr('services.%s.%s' %(self.service_type,service_name))
        return dict(conf) if conf else {}

    @property
    def implementations(self):
        if not hasattr(self,'_implementations'):
            self._implementations = {}
            dirs = self.site.resource_loader.getResourceList(self.site.resources_dirs, 'services/%s' %(self.service_type))
            dirs.reverse()
            self.baseImplementation = None
            for d in dirs:
                for impl in os.listdir(d):
                    implname,implext = os.path.splitext(impl)
                    impl = os.path.join(d,impl)
                    if os.path.isdir(impl):
                        impl = os.path.join(d,impl,'service.py')
                        if not os.path.exists(impl):
                            continue
                        implext = '.py'
                    if implext!='.py':
                        continue
                    try:
                        module = gnrImport(impl,avoidDup=True)
                        service_class = getattr(module,'Service',None) or getattr(module,'Main',None) #backward compatibility
                        self._implementations[implname] =  service_class
                    except ImportError as imperr:
                        log.exception("Could not import %s"%impl)
                        log.exception(str(imperr))
                    
                    if not self.baseImplementation:
                        self.baseImplementation = implname

        return self._implementations

    def getServiceFactory(self,implementation=None):
        return self.implementations.get(implementation) or self.implementations.get(self.baseImplementation)
    
    @property
    def default_service_name(self):
        return self.service_type

    def __call__(self, service_name=None, **kwargs):
        service_name = service_name or self.default_service_name
        service = self.service_instances.get(service_name)
        gs = self.site.register.globalStore()
        cache_key = 'globalServices_lastTS.%s_%s' %(self.service_type,service_name)
        lastTS = gs.getItem(cache_key)
        if service is None or (lastTS and service._service_creation_ts<lastTS):
            service = self.addService(service_name, **kwargs)
            if service:
                service._service_creation_ts = datetime.now()
                with self.site.register.globalStore() as gs:
                    gs.setItem(cache_key,service._service_creation_ts)
        return service



class GnrBaseService(object):
    def __init__(self, parent):
        self.parent = parent
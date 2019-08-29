# -*- coding: utf-8 -*-
#from builtins import object
from gnr.core.gnrbag import Bag
import inspect
import os
import sys
from gnr.lib.services import GnrBaseService
from gnr.core.gnrlang import  gnrImport



class StorageHandler(object):
    def __init__(self, site=None):
        self.site = site
        self.storages = dict()

    
    def addAllStorages(self):
        storages = self.site.db.table('sys.services').query(where="$service_type='storage'").fetch()
        for storage_conf in storages:
            implementation = storage_conf['implementation']
            storage_name = storage_conf['service_name']
            self.site.services.get('%s:%s'%(storage_name,implementation)) 
        pass

    def add(self, storage_name, storage_service_factory, **kwargs):
        storage = storage_service_factory(self.site, **kwargs)
        self.storages[storage_name] = storage

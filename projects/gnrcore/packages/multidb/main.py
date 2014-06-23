#!/usr/bin/env python
# encoding: utf-8
from gnr.app.gnrdbo import GnrDboTable, GnrDboPackage, Table_counter

class Package(GnrDboPackage):
    def config_attributes(self):
        return dict(comment='multidb package',sqlschema='multidb',
                name_short='Multidb', name_long='Multidb', name_full='Multidb')

    def config_db(self, pkg):
        pass
    
    def copyTableToStore(self,):
        pass


class Table(GnrDboTable):
    def use_dbstores(self,**kwargs):
        return False

#!/usr/bin/env python
# encoding: utf-8
from gnr.app.gnrdbo import GnrDboTable, GnrDboPackage, Table_counter

class Package(GnrDboPackage):
    def config_attributes(self):
        return dict(comment='task package',sqlschema='task',
                    name_short='Task', name_long='Task', name_full='Task')
                    
    def config_db(self, pkg):
        pass
        
    def loginUrl(self):
        return 'task/login'
        
class Table(GnrDboTable):
    pass

#!/usr/bin/env python
# encoding: utf-8
from gnr.app.gnrdbo import GnrDboTable, GnrDboPackage, Table_counter

class Package(GnrDboPackage):
    def config_attributes(self):
        return dict(comment='email package',sqlschema='email',
                name_short='Email', name_long='Email', name_full='Email')
                
    def config_db(self, pkg):
        pass
        
    def loginUrl(self):
        return 'email/login'
        
class Table(GnrDboTable):
    pass

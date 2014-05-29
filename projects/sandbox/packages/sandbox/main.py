#!/usr/bin/env python
# encoding: utf-8
from gnr.app.gnrdbo import GnrDboTable, GnrDboPackage

class Package(GnrDboPackage):
    def config_attributes(self):
        return dict(comment='sandbox package',sqlschema='sandbox',
                    name_short='Sandbox', name_long='Sandbox', name_full='Sandbox')
                    
    def config_db(self, pkg):
        pass
        
class Table(GnrDboTable):
    pass

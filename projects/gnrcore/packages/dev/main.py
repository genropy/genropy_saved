#!/usr/bin/env python
# encoding: utf-8
from gnr.app.gnrdbo import GnrDboTable, GnrDboPackage

class Package(GnrDboPackage):
    def config_attributes(self):
        return dict(comment='dev package',sqlschema='dev',
                    name_short='Dev', name_long='Dev', name_full='Dev')
                    
    def config_db(self, pkg):
        pass
        
class Table(GnrDboTable):
    pass

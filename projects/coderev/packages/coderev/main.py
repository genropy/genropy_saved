#!/usr/bin/env python
# encoding: utf-8
from gnr.app.gnrdbo import GnrDboTable, GnrDboPackage

class Package(GnrDboPackage):
    def config_attributes(self):
        return dict(comment='coderev package',sqlschema='coderev',
                    name_short='Coderev', name_long='Coderev', name_full='Coderev')
                    
    def config_db(self, pkg):
        pass
        
class Table(GnrDboTable):
    pass

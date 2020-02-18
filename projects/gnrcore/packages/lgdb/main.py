#!/usr/bin/env python
# encoding: utf-8
from gnr.app.gnrdbo import GnrDboTable, GnrDboPackage

class Package(GnrDboPackage):
    def config_attributes(self):
        return dict(comment='Legacy db', sqlschema='lgdb',sqlprefix=True,
                    name_short='Legacy db', name_long='Legacy db analyzer')
                    
    def config_db(self, pkg):
        pass
        
class Table(GnrDboTable):
    pass

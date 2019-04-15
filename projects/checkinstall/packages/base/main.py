#!/usr/bin/env python
# encoding: utf-8
from gnr.app.gnrdbo import GnrDboTable, GnrDboPackage

class Package(GnrDboPackage):
    def config_attributes(self):
        return dict(comment='test package',sqlschema='test',sqlprefix=True,
                    name_short='Test', name_long='Test', name_full='Test')
                    
    def config_db(self, pkg):
        pass
        
class Table(GnrDboTable):
    pass

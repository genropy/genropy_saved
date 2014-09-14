#!/usr/bin/env python
# encoding: utf-8
from gnr.app.gnrdbo import GnrDboTable, GnrDboPackage

class Package(GnrDboPackage):
    def config_attributes(self):
        return dict(comment='docker package',sqlschema='docker',
                    name_short='Docker', name_long='Docker', name_full='Docker')
                    
    def config_db(self, pkg):
        pass
        
class Table(GnrDboTable):
    pass

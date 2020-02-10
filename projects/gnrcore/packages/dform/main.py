#!/usr/bin/env python
# encoding: utf-8
from gnr.app.gnrdbo import GnrDboTable, GnrDboPackage

class Package(GnrDboPackage):
    def config_attributes(self):
        return dict(comment='dform package',sqlschema='dform',sqlprefix=True,
                    name_short='Dform', name_long='Dform', name_full='Dform')
                    
    def config_db(self, pkg):
        pass
        
class Table(GnrDboTable):
    pass

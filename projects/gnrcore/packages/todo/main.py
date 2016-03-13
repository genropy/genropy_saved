#!/usr/bin/env python
# encoding: utf-8
from gnr.app.gnrdbo import GnrDboTable, GnrDboPackage

class Package(GnrDboPackage):
    def config_attributes(self):
        return dict(comment='todo package',sqlschema='todo',sqlprefix=True,
                    name_short='Todo', name_long='To Do', name_full='Todo')
                    
    def config_db(self, pkg):
        pass
        
class Table(GnrDboTable):
    pass

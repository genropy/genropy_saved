#!/usr/bin/env python
# encoding: utf-8
from gnr.app.gnrdbo import GnrDboTable, GnrDboPackage, Table_counter, Table_userobject

class Package(GnrDboPackage):
    def config_attributes(self):
        return dict(sqlschema='showcase',
                    comment='Showcase',
                    name_short='showcase',
                    name_long='showcase',
                    name_full='showcase')

    def config_db(self, pkg):
        pass
        
class Table(GnrDboTable):
    pass
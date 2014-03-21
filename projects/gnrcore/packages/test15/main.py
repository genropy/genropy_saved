#!/usr/bin/env python
# encoding: utf-8
from gnr.app.gnrdbo import GnrDboTable, GnrDboPackage, Table_counter

class Package(GnrDboPackage):
    def config_attributes(self):
        return dict(comment='test15 package', sqlschema='test15',
                    name_short='Test15', name_long='Test15', name_full='Test15',_syspackage=True)

    def config_db(self, pkg):
        pass

    def loginUrl(self):
        return 'test15/login'

class Table(GnrDboTable):
    pass

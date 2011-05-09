#!/usr/bin/env python
# encoding: utf-8
from gnr.app.gnrdbo import GnrDboTable, GnrDboPackage, Table_counter, Table_userobject

class Package(GnrDboPackage):
    def config_attributes(self):
        return dict(comment='portal package', sqlschema='portal',
                    name_short='Portal', name_long='Portal', name_full='Portal')

    def config_db(self, pkg):
        pass

    def loginUrl(self):
        return 'portal/login'

class Table(GnrDboTable):
    pass

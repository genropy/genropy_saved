#!/usr/bin/env python
# encoding: utf-8
from gnr.app.gnrdbo import GnrDboTable, GnrDboPackage, Table_counter, Table_userobject

class Package(GnrDboPackage):
    def config_attributes(self):
        return dict(comment='warh package', sqlschema='warh',
                    name_short='Warh', name_long='Warh', name_full='Warh')

    def config_db(self, pkg):
        pass

    def loginUrl(self):
        return 'warh/login'

class Table(GnrDboTable):
    pass

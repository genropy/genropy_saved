#!/usr/bin/env python
# encoding: utf-8
from gnr.app.gnrdbo import GnrDboTable, GnrDboPackage
from gnr.app.gnrdbo import Table_counter     # auto build the table counter
from gnr.app.gnrdbo import Table_userobject  # auto build the table userobject

class Package(GnrDboPackage):
    def config_attributes(self):
        return dict(sqlschema='invc',
                    comment='gestione fatture',
                    name_short='invoices',
                    name_long='invoices')

    def config_db(self, pkg):
        pass

class Table(GnrDboTable):
    pass






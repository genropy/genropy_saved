#!/usr/bin/env python
# encoding: utf-8
from gnr.app.gnrdbo import GnrDboTable, GnrDboPackage
from gnr.app.gnrdbo import Table_counter     # auto build the table counter
from gnr.app.gnrdbo import Table_userobject  # auto build the table userobject

class Package(GnrDboPackage):
    def config_attributes(self):
        return dict(sqlschema='invc',comment='invoice manager',
                    name_short='invoices',name_long='invoices',full_name='Invoice')
                    
    def config_db(self, pkg):
        pass
        
    def loginUrl(self):
        return 'invoice/login'

    def custom_type_money(self):
        return dict(dtype='N', size='10,3')

class Table(GnrDboTable):
    pass






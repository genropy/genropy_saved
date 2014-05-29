#!/usr/bin/env python
# encoding: utf-8
from gnr.app.gnrdbo import GnrDboTable, GnrDboPackage

class Package(GnrDboPackage):
    def config_attributes(self):
        return dict(comment='Package demo fatturazione',sqlschema='fatt',
                    name_short='Fatturazione', name_long='Fatturazione', name_full='Fatturazione')
                    
    def config_db(self, pkg):
        pass

    def custom_type_money(self):
        return dict(dtype='N',format='#,###.00')

    def custom_type_percent(self):
        return dict(dtype='N',format='#,###.00')
        
class Table(GnrDboTable):
    pass

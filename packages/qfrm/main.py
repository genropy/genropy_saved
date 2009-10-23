#!/usr/bin/env python
# encoding: utf-8

from gnr.app.gnrdbo import GnrDboTable, GnrDboPackage, Table_counter, Table_userobject
from datetime import datetime

class Package(GnrDboPackage):
    
    def config_attributes(self):
        return dict(sqlschema='qfrm',
                    comment='qfrm',
                    name_short='qfrm',
                    name_long='!!Quick Form',
                    name_full='!!Quick Form Package')
    
    def config_db(self, pkg):
        pass




class Table(GnrDboTable):
    pass

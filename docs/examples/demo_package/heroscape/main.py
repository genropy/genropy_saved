#!/usr/bin/env python
# encoding: utf-8


import os

from gnr.core.gnrbag import Bag

from gnr.app.gnrdbo import GnrDboTable, GnrDboPackage, Table_counter
from gnr.core.gnrstring import templateReplace, splitAndStrip

class Package(GnrDboPackage):
    def config_attributes(self):
        return dict(sqlschema='heroscape',comment='heroscape package',
                name_short='heroscape', name_long='heroscape', name_full='heroscape')
        
    def config_db(self, pkg):
        pass
        

class Table(GnrDboTable):
    pass
    
    

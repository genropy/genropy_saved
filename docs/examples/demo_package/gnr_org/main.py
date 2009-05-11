#!/usr/bin/env python
# encoding: utf-8


import os

from gnr.core.gnrbag import Bag

from gnr.app.gnrdbo import GnrDboTable, GnrDboPackage, Table_counter
from gnr.core.gnrstring import templateReplace, splitAndStrip

class Package(GnrDboPackage):
    def config_attributes(self):
        return dict(comment='gnr_org package',
                name_short='gnr_org', name_long='gnr_org', name_full='gnr_org')
        
    def config_db(self, pkg):
        pass
        

class Table(GnrDboTable):
    pass
    
    

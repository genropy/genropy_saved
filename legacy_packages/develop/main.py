#!/usr/bin/env python
# encoding: utf-8
import os

from gnr.core.gnrbag import Bag

from gnr.app.gnrdbo import GnrDboTable, GnrDboPackage, Table_counter, Table_userobject
from gnr.core.gnrstring import templateReplace, splitAndStrip

class Package(GnrDboPackage):
    def config_attributes(self):
        return dict(comment='develop package',
                    name_short='develop',
                    name_long='develop',
                     name_full='develop')
        
    def config_db(self, pkg):
        pass

class Table(GnrDboTable):
    pass

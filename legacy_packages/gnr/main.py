#!/usr/bin/env python
# encoding: utf-8
"""
main.py

Created by Saverio Porcari on 2007-05-10.
Copyright (c) 2007 __MyCompanyName__. All rights reserved.
"""

import sys
import os
import datetime

from gnr.core.gnrbag import Bag
from gnr.app.gnrdbo import GnrDboTable, GnrDboPackage

class Package(GnrDboPackage):
    def config_attributes(self):
        return dict(sqlschema='gnr', comment='Transaction Manager',name_short='Transaction Manager', 
                    reserved='y',_syspackage=True)   

class Table(GnrDboTable):
    pass     

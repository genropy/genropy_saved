#!/usr/bin/env python
# encoding: utf-8

from gnr.app.gnrdbo import GnrDboTable, GnrDboPackage

class Package(GnrDboPackage):
    def config_attributes(self):
        return dict(comment='A package for video catalog management',
            name_short='cinema',
            name_long='Video Catalog', 
            name_full='Video Catalog',
            main_schema='cinema')
            

class Table(GnrDboTable):
    pass


            

        
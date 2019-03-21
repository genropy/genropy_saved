#!/usr/bin/env python
# encoding: utf-8
from gnr.app.gnrdbo import GnrDboTable, GnrDboPackage

class Package(GnrDboPackage):
    def config_attributes(self):
        return dict(comment='Biz package',sqlschema='biz',sqlprefix=True,
                    name_short='Business Intelligence', name_long='Business Intelligence', name_full='Business Intelligence')
                    
    def config_db(self, pkg):
        pass
        
    def required_packages(self):
        return ['gnrcore:adm']

class Table(GnrDboTable):
    pass

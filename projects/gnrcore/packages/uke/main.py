#!/usr/bin/env python
# encoding: utf-8
from gnr.app.gnrdbo import GnrDboTable, GnrDboPackage, Table_sync_event


class Package(GnrDboPackage):
    def config_attributes(self):
        return dict(comment='Unified Knowledge Environment',sqlschema='uke',
                    name_short='uke', name_long='UKE', name_full='Unified Knowledge Environment')
        
class Table(GnrDboTable):
    pass
        
        

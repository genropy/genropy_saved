#!/usr/bin/env python
# encoding: utf-8
from gnr.app.gnrdbo import GnrDboTable, GnrDboPackage, Table_counter

class Package(GnrDboPackage):
    def config_attributes(self):
        return dict(comment='website package',sqlschema='website',
                name_short='Website', name_long='Website', name_full='Website')

    def config_db(self, pkg):
        pass

    def loginUrl(self):
        return 'website/login'

class Table(GnrDboTable):
    pass

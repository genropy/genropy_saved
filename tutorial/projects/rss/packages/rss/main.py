#!/usr/bin/env python
# encoding: utf-8
from gnr.app.gnrdbo import GnrDboTable, GnrDboPackage, Table_counter, Table_userobject

class Package(GnrDboPackage):
    def config_attributes(self):
        return dict(comment='rss package', sqlschema='rss',
                    name_short='Rss', name_long='Rss', name_full='Rss')

    def config_db(self, pkg):
        pass

    def loginUrl(self):
        return 'rss/login'

class Table(GnrDboTable):
    pass

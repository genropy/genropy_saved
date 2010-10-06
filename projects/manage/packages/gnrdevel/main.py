#!/usr/bin/env python
# encoding: utf-8
from gnr.app.gnrdbo import GnrDboTable, GnrDboPackage, Table_counter, Table_userobject

class Package(GnrDboPackage):
    def config_attributes(self):
        return dict(comment='gnrdevel package',sqlschema='gnrdevel',
                name_short='Gnrdevel', name_long='Gnrdevel', name_full='Gnrdevel')

    def config_db(self, pkg):
        pass

    def loginUrl(self):
        return 'gnrdevel/login'

class Table(GnrDboTable):
    pass

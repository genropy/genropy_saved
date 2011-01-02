#!/usr/bin/env python
# encoding: utf-8
from gnr.app.gnrdbo import GnrDboTable, GnrDboPackage, Table_counter, Table_userobject

class Package(GnrDboPackage):
    def config_attributes(self):
        return dict(comment='gnrtest package', sqlschema='gnrtest', name_short='Gnrtest',
                    name_long='GenroPy Test Package',
                    name_full='GenroPy Test Package')

    def config_db(self, pkg):
        pass

    def loginUrl(self):
        return 'adm/login'

class Table(GnrDboTable):
    pass

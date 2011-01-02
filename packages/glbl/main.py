#!/usr/bin/env python
# encoding: utf-8
from gnr.app.gnrdbo import GnrDboTable, GnrDboPackage, Table_counter, Table_userobject


class Package(GnrDboPackage):
    def config_attributes(self):
        return dict(sqlschema='glbl',
                    comment='glbl package',
                    name_short='glbl',
                    name_long='glbl',
                    name_full='glbl')

    def config_db(self, pkg):
        pass


class Table(GnrDboTable):
    pass





#!/usr/bin/env python
# encoding: utf-8
from gnr.app.gnrdbo import GnrDboTable, GnrDboPackage, Table_counter, Table_recordtag, Table_recordtag_link


class Package(GnrDboPackage):
    def config_attributes(self):
        return dict(comment='flib package', sqlschema='flib',
                    name_short='Flib', name_long='Flib', name_full='Flib')

class Table(GnrDboTable):
    pass

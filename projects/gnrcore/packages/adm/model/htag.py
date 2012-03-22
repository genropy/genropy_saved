#!/usr/bin/env python
# encoding: utf-8
from gnr.app.gnrdbo import GnrHTable

class Table(GnrHTable):
    def config_db(self, pkg):
        tbl = pkg.table('htag', pkey='id', name_long='!!Tag',
                        rowcaption='$code,$description',
                        newrecord_caption='!!New tag')
        self.sysFields(tbl)
        self.htableFields(tbl)
        tbl.column('isreserved', 'B', name_long='!!Reserved')
        tbl.column('note',name_long='!!Notes')


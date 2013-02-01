#!/usr/bin/env python
# encoding: utf-8

class Table(object):
    def config_db(self, pkg):
        tbl = pkg.table('letterhead_type', pkey='code', name_long='Letterhead type', name_plural='Letterhead types',lookup=True)
        self.sysFields(tbl,id=False)
        tbl.column('code',name_long='!!Code',unique=True,indexed=True,validate_notnull='Required')
        tbl.column('description',name_long='!!Description')
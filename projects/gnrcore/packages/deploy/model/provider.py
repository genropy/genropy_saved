#!/usr/bin/env python
# encoding: utf-8

class Table(object):
    def config_db(self, pkg):
        tbl = pkg.table('provider',
                        pkey='code',
                        name_long='Service provider',
                        name_plural='Service providers')
        self.sysFields(tbl, id=False)
        tbl.column('code' , size=':10',name_long='!!Code')
        tbl.column('description',name_long='!!Description')
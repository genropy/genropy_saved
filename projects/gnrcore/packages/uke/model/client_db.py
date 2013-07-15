#!/usr/bin/env python
# encoding: utf-8

class Table(object):
    def config_db(self, pkg):
        tbl = pkg.table('client_db', pkey='id', name_long='Client database', name_plural='!!Client databases')
        self.sysFields(tbl)
        tbl.column('name' ,name_long='!!Name')
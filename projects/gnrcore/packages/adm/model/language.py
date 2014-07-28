#!/usr/bin/env python
# encoding: utf-8

class Table(object):
    def config_db(self, pkg):
        tbl = pkg.table('language', pkey='id', name_long='Language', name_plural='!!Languages',lookup=True)
        self.sysFields(tbl,counter=True)
        tbl.column('code' ,size=':2',name_long='!!Code')
        tbl.column('name' ,name_long='!!Name')

    
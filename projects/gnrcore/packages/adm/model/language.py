#!/usr/bin/env python
# encoding: utf-8

class Table(object):
    def config_db(self, pkg):
        tbl = pkg.table('language', pkey='code', name_long='Language', name_plural='!!Languages',lookup=True,caption_field='name')
        self.sysFields(tbl,counter=True,id=False)
        tbl.column('code' ,size=':2',name_long='!!Code',unique=True)
        tbl.column('name' ,name_long='!!Name')

    
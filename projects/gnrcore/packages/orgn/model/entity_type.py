#!/usr/bin/env python
# encoding: utf-8

class Table(object):
    def config_db(self, pkg):
        tbl = pkg.table('entity_type', pkey='code', name_long='!!Entity type', name_plural='!!Entity types',
                        caption_field='description')
        self.sysFields(tbl,id=False,df=True)
        tbl.column('code' ,size=':15',name_long='!!Code')
        tbl.column('description' ,size=':40',name_long='!!Description')
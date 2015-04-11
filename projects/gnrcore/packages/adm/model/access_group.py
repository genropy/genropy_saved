#!/usr/bin/env python
# encoding: utf-8

class Table(object):
    def config_db(self, pkg):
        tbl = pkg.table('access_group', pkey='code', name_long='!!Access group', 
                        name_plural='!!Access group',caption_field='code')
        self.sysFields(tbl,id=False)
        tbl.column('code' ,size=':10',name_long='!!Code')
        tbl.column('description' ,size=':30',name_long='!!Description')
        tbl.column('allowed_ip',name_long='!!Allowed ip')

#!/usr/bin/env python
# encoding: utf-8

class Table(object):
    def config_db(self,pkg):
        tbl=pkg.table('message_type', pkey='code', name_long='!!Message type', 
                        name_plural='!!Message types',caption_field='description',lookup=True)
        self.sysFields(tbl)
        tbl.column('code', size=':10', name_long='!!Code')
        tbl.column('description', size=':40', name_long='!!Description')
        
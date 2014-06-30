#!/usr/bin/env python
# encoding: utf-8

class Table(object):
    def config_db(self, pkg):
        tbl = pkg.table('ticket_type', pkey='code', name_long='!!Ticket type', name_plural='!!Ticket types',caption_field='code')
        self.sysFields(tbl,id=False,df=True)
        tbl.column('code' ,size=':10',name_long='!!Code',indexed=True)
        tbl.column('description' ,size=':20',name_long='!!Description',indexed=True)
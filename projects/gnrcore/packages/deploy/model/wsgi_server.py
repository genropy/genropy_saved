#!/usr/bin/env python
# encoding: utf-8

class Table(object):
    def config_db(self, pkg):
        tbl = pkg.table('wsgi_server', pkey='code', name_long='!!WSGI server', name_plural='!!WSGI servers', lookup=True)
        self.sysFields(tbl, id=False)
        tbl.column('code' , size=':10',name_long='!!Code')
        tbl.column('description',name_long='!!Description')
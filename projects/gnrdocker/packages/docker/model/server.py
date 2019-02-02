#!/usr/bin/env python
# encoding: utf-8

from builtins import object
class Table(object):
    def config_db(self, pkg):
        tbl = pkg.table('server', pkey='id', name_long='!!Server', name_plural='!!Servers',caption_field='name')
        self.sysFields(tbl)
        tbl.column('name',name_long='!!Name')
        tbl.column('host',name_long='!!Host')

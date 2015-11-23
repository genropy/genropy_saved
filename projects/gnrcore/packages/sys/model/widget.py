#!/usr/bin/env python
# encoding: utf-8

class Table(object):
    def config_db(self, pkg):
        tbl = pkg.table('widget', pkey='id', name_long='!!Widget', 
                        name_plural='!!Widgets',caption_field='name',audit='lazy')
        self.sysFields(tbl,hierarchical='name',df=True)
        tbl.column('name',name_long='!!Name')
        tbl.column('server',dtype='B',name_long='!!Server')


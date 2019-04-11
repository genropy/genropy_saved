#!/usr/bin/env python
# encoding: utf-8

from builtins import object
class Table(object):
    def config_db(self, pkg):
        tbl = pkg.table('group', pkey='code', name_long='Group', 
                        name_plural='!!Groups',caption_field='description')
        self.sysFields(tbl, id=False,counter=True)
        tbl.column('code' ,size=':15',name_long='!!Code',unmodifiable=True)
        tbl.column('description' ,name_long='!!Description')
        tbl.column('custom_menu', dtype='X', name_long='!!Custom menu')
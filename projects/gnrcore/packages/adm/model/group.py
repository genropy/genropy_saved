#!/usr/bin/env python
# encoding: utf-8

class Table(object):
    def config_db(self, pkg):
        tbl = pkg.table('group', pkey='code', name_long='Group', 
                        name_plural='!!Groups',caption_field='description')
        self.sysFields(tbl, id=False,useProtectionTag='system',counter=True)
        tbl.column('code' ,name_long='!!Code')
        tbl.column('description' ,name_long='!!Description')

#!/usr/bin/env python
# encoding: utf-8

from builtins import object
class Table(object):
    def config_db(self, pkg):
        tbl = pkg.table('container', pkey='id', name_long='!!Container', name_plural='!!Containers',caption_field='name')
        self.sysFields(tbl)
        tbl.column('name',name_long='!!Name')
        tbl.column('image_id',size='22' ,group='_',name_long='!!Image').relation('image.id',relation_name='containers',mode='foreignkey',onDelete='raise')
        tbl.column('status' ,size=':1',name_long='!!Status')
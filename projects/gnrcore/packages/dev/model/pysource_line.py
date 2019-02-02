#!/usr/bin/env python
# encoding: utf-8

from builtins import object
class Table(object):
    def config_db(self, pkg):
        tbl = pkg.table('pysource_line', pkey='id', name_long='!!Source line')
        self.sysFields(tbl)
        tbl.column('pysource_id',size='22' ,group='_',name_long='!!Pysource').relation('pysource.id',relation_name='lines',mode='foreignkey',onDelete='cascade')
        tbl.column('linenum',dtype='I',name_long='!!Line')
        tbl.column('source',name_long='!!Source')
        tbl.column('comment',name_long='!!Comment')
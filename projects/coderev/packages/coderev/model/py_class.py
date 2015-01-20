#!/usr/bin/env python
# encoding: utf-8

class Table(object):
    def config_db(self, pkg):
        tbl = pkg.table('py_class', pkey='id', name_long='Class', name_plural='!!Class',caption_field='name')
        self.sysFields(tbl)
        tbl.column('name' ,name_long='!!Name',name_short='Name')
        tbl.column('py_module_id',	size='22' ,group='_',name_long='!!Module').relation('py_module.id',
        	                                                                    relation_name='classes',
        	                                                                    mode='foreignkey',
        	                                                                    onDelete='cascade')
        tbl.column('docline', name_long='!!Docline')
        tbl.column('inherit_from', name_long='!!Inherit From')
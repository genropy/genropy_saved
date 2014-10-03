#!/usr/bin/env python
# encoding: utf-8

class Table(object):
    def config_db(self, pkg):
        tbl = pkg.table('py_method', pkey='id', name_long='Method', name_plural='!!Methods',caption_field='name')
        self.sysFields(tbl)
        tbl.column('name', name_long='!!Name')
        tbl.column('py_module_id',	size='22' ,group='_',name_long='!!Module').relation('py_module.id',
                                                                            relation_name='methods',
                                                                            mode='foreignkey',
                                                                            onDelete='cascade')
        tbl.column('py_class_id',size='22' ,group='_',name_long='!!Class').relation('py_class.id',
                                                                            relation_name='methods',
                                                                            mode='foreignkey',
                                                                            onDelete='cascade')
        tbl.column('private',dtype='B',name_long='!!Private')
        tbl.column('docline', name_long='!!Docline')
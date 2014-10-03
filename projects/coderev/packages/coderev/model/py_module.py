#!/usr/bin/env python
# encoding: utf-8

class Table(object):
    def config_db(self, pkg):
        tbl = pkg.table('py_module', pkey='id', name_long='Module', name_plural='!!Modules',caption_field='name')
        self.sysFields(tbl)
        tbl.column('name' ,name_long='!!Name',name_short='Name')
        tbl.column('py_package_id', size='22' ,group='_',name_long='!!Package').relation('py_package.id',
                                                                                relation_name='modules',
                                                                                mode='foreignkey',
                                                                                onDelete='cascade')
        tbl.column('docline', name_long='!!Docline')
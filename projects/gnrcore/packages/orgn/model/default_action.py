#!/usr/bin/env python
# encoding: utf-8

from builtins import object
class Table(object):
    def config_db(self, pkg):
        tbl = pkg.table('default_action', pkey='id', name_long='!!Default action', 
                        name_plural='!!Default actions')
        self.sysFields(tbl)
        tbl.column('annotation_type_id',size='22' ,group='_',name_long='!!Annotation type'
                            ).relation('annotation_type.id',relation_name='default_actions',mode='foreignkey',onDelete='cascade')
        tbl.column('action_type_id',size='22' ,group='_',name_long='!!Action type').relation('action_type.id',relation_name='annotation_default_actions',
                                                                                                mode='foreignkey',onDelete='raise')
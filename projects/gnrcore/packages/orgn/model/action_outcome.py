#!/usr/bin/env python
# encoding: utf-8

class Table(object):
    def config_db(self, pkg):
        tbl = pkg.table('action_outcome', pkey='id', name_long='!!Action outcome', name_plural='!!Outcomes')
        self.sysFields(tbl,counter='action_type_id')
        tbl.column('action_type_id',size='22' ,group='_',name_long='!!Action type').relation('action_type.id',relation_name='outcomes',mode='foreignkey',onDelete='raise')
        tbl.column('outcome_action_type_id',size='22' ,group='_',name_long='!!Overcome').relation('action_type.id',mode='foreignkey',onDelete='raise')
        tbl.column('deadline_days',dtype='I',name_long='!!Deadline days',name_short='!!D.Days')
        tbl.column('default_tag',name_long='!!Default tag')
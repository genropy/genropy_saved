#!/usr/bin/env python
# encoding: utf-8

class Table(object):
    def config_db(self, pkg):
        tbl = pkg.table('entity', pkey='id', name_long='!!Entity', 
                        name_plural='!!Entities',
                        caption_field='description')
        self.sysFields(tbl)
        tbl.column('type_code',size=':15' ,group='_',name_long='!!Type').relation('entity_type.code',relation_name='entities',
                                                                                    mode='foreignkey',onDelete='raise')  
        tbl.column('description' ,size=':40',name_long='!!Description')
        tbl.column('entity_fields',dtype='X',name_long='!!Fields',subfields='type_code')
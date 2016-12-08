#!/usr/bin/env python
# encoding: utf-8

class Table(object):
    def config_db(self, pkg):
        tbl = pkg.table('user_attention', pkey='id', name_long='!!User attention', name_plural='!!User attentions',caption_field='')
        self.sysFields(tbl)
        tbl.column('user_id',size='22' ,group='_',
            name_long='!!User').relation('adm.user.id',
            relation_name='attentions',mode='foreignkey',onDelete='cascade')
        tbl.column('annotation_id',size='22' ,group='_',name_long='!!Annotation').relation('annotation.id',relation_name='attention_users',
                        mode='foreignkey',onDelete='cascade')
        tbl.column('confirm_ts',dtype='DH',name_long='!!Confirm ts')
        tbl.column('note',name_long='!!Note')
        tbl.formulaColumn('pending_for_user',"$user_id=:env_user_id AND $confirm_ts IS NULL",
            dtype='B')
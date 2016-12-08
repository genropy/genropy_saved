#!/usr/bin/env python
# encoding: utf-8

class Table(object):
    def config_db(self, pkg):
        tbl = pkg.table('default_attention', pkey='id', name_long='!!Default attention', name_plural='!!Default attention',
                        caption_field='caption')
        self.sysFields(tbl)
        tbl.column('user_id',size='22' ,group='_',name_long='!!User').relation('adm.user.id',relation_name='default_attentions',mode='foreignkey',onDelete='cascade')
        tbl.column('group_code',size=':15' ,group='_',name_long='!!Group').relation('adm.group.code',
                        relation_name='default_attentions',mode='foreignkey',onDelete='cascade')
        tbl.column('tag_id',size='22',group='_',name_long='Tag id').relation('adm.htag.id', mode='foreignkey', onDelete='cascade',
                                                                          relation_name='default_attentions')
        tbl.column('annotation_type_id',size='22' ,
                    group='_',name_long='!!Annotation type').relation('annotation_type.id',
                    relation_name='default_attentions',mode='foreignkey',onDelete='cascade')
        tbl.formulaColumn('caption',"""(CASE WHEN $user_id IS NOT NULL THEN @user_id.username
                                             WHEN $group_code IS NOT NULL THEN $group_code
                                             ELSE @tag_id.hierarchical_description 
                                        END)""")
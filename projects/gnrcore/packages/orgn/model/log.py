#!/usr/bin/env python
# encoding: utf-8

class Table(object):
    def config_db(self, pkg):
        tbl = pkg.table('log', pkey='id', name_long='!!Log', name_plural='!!Logs',caption_field='subject')
        self.sysFields(tbl)
        tbl.column('description',name_long='!!Description')
        tbl.column('log_type_id',size='22' ,group='_',name_long='!!Log type').relation('log_type.id',relation_name='logs',
                                                                                        mode='foreignkey',onDelete='raise') 
        tbl.column('log_fields',dtype='X',name_long='!!Fields',subfields='log_type_id')
        tbl.column('date',dtype='D',name_long='!!Date')
        tbl.column('time',dtype='H',name_long='!!Time')
        tbl.column('user_id',size='22',group='_',name_long='User').relation('adm.user.id',
                                                                            relation_name='orgn_log',onDelete='raise')



    def defaultValues(self):
        return dict(user_id=self.db.currentEnv.get('user_id'))
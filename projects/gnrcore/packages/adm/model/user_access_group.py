#!/usr/bin/env python
# encoding: utf-8

class Table(object):
    def config_db(self, pkg):
        tbl = pkg.table('user_access_group', pkey='id', name_long='!!User access', name_plural='!!User access')
        self.sysFields(tbl)
        tbl.column('user_id',size='22' ,group='_',name_long='!!User').relation('user.id',relation_name='access_groups',
                                                                                mode='foreignkey',onDelete='cascade')
        tbl.column('access_group_code',size=':10' ,group='_',name_long='!!Access group').relation('access_group.code',
                                                                                                    relation_name='access_users',
                                                                                                    mode='foreignkey',onDelete='cascade')                                   
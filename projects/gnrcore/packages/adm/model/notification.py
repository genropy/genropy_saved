#!/usr/bin/env python
# encoding: utf-8

class Table(object):
    def config_db(self, pkg):
        tbl = pkg.table('notification', pkey='id', name_long='!!Notification', name_plural='!!Notifications',caption_field='title')
        self.sysFields(tbl)
        tbl.column('title' ,name_long='!!Title')
        tbl.column('template','X',name_long='!!Template')
        tbl.column('confirm_label',name_long='!!Confirm label')
        tbl.column('tag_rule',name_long='!!Tag rule')
        tbl.column('all_users','B',name_long='!!For all users')
        tbl.column('letterhead_id',size='22',group='_',name_long='!!Letterhead').relation('htmltemplate.id',relation_name='notifications',mode='foreignkey')
        tbl.formulaColumn('existing_for_current_user',"""
                (EXISTS(SELECT * FROM adm.adm_user_notification AS un WHERE un.user_id=:env_user_id AND un.notification_id=#THIS.id))
            """,dtype='B')

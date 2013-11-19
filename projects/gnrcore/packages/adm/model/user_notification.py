#!/usr/bin/env python
# encoding: utf-8

from gnr.core.gnrdecorator import public_method
from gnr.web.gnrbaseclasses import TableTemplateToHtml
from gnr.core.gnrbag import Bag


class Table(object):
    def config_db(self, pkg):
        tbl = pkg.table('user_notification', pkey='id', name_long='User notification', name_plural='!!User notifications')
        self.sysFields(tbl)
        tbl.column('user_id',size='22' ,group='_',name_long='!!User').relation('user.id',relation_name='user_notifications',mode='foreignkey',onDelete='raise')
        tbl.column('notification_id',size='22' ,group='_',name_long='!!User').relation('notification.id',relation_name='notification_users',mode='foreignkey',onDelete='raise')
        tbl.column('confirmed',dtype='B',name_long='!!Confirmed')


    @public_method
    def getNotification(self,pkey=None):
        user_id,notification_template,notification_title,confirm_label,letterhead_id = self.readColumns(pkey=pkey,columns="""$user_id,@notification_id.template,@notification_id.title,
                                                                                                                                 @notification_id.confirm_label,@notification_id.letterhead_id""")
        usertbl = self.db.table('adm.user')
        source_record = usertbl.record(pkey=user_id).output('bag')
        htmlbuilder = TableTemplateToHtml(usertbl)
        notification = htmlbuilder(record=source_record,template=Bag(notification_template)['compiled'],letterhead_id=letterhead_id,pdf=False)
        return dict(notification=notification,title=notification_title,confirm_label=confirm_label)


    @public_method
    def confirmNotification(self,pkey=None):
        user_notification = self.record(pkey=pkey,for_update=True).output('dict')
        oldrec = dict(user_notification)
        user_notification['confirmed'] = True
        self.update(user_notification,oldrec)
        self.db.commit()
        return self.nextUserNotification(user_notification['user_id'])

    def nextUserNotification(self,user_id=None):
        f = self.query(where='$user_id=:uid AND $confirmed IS NOT TRUE',uid=user_id,limit=1,order_by='$__ins_ts asc').fetch()
        user_notification_id = f[0]['id'] if f else None
        if user_notification_id:
            return user_notification_id
        

    def updateGenericNotification(self,user_id=None,user_tags=None):
        generic_notification = self.db.table('adm.notification').query(where="""($all_users IS TRUE OR $tag_rule IS NOT NULL )
                                                                                AND NOT $existing_for_current_user
                                                                                """,env_user_id=user_id).fetch()
        commit = False
        for n in generic_notification:
            if n['all_users'] or self.db.application.checkResourcePermission(n['tag_rule'],user_tags):
                commit = True
                self.insert(dict(user_id=user_id,notification_id=n['id']))
        if commit:
            self.db.commit()









        
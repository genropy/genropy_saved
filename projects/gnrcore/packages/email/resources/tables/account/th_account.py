#!/usr/bin/python
# -*- coding: UTF-8 -*-

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method


class View(BaseComponent):

    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('account_name',width='35em')
        r.fieldcell('address',width='35em')
        r.fieldcell('full_name',width='80em')
        r.fieldcell('host',width='80em')
        r.fieldcell('port',width='7em')
        r.fieldcell('protocol_code',width='35em')
        r.fieldcell('tls',width='7em')
        r.fieldcell('ssl',width='7em')
        r.fieldcell('username',width='80em')
        r.fieldcell('password',width='80em')
        r.fieldcell('last_uid',width='7em')
        return struct

    def th_order(self):
        return 'account_name'

    def th_query(self):
        return dict(column='account_name',op='contains', val='',runOnStart=False)

    def th_dialog(self):
        return dict(height='400px',width='600px')
        
class ViewSmall(BaseComponent):
    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('account_name',width='100%')
        
    def th_order(self):
        return 'account_name'

class Form(BaseComponent):

    def th_form(self, form):
        tc = form.center.tabContainer()
        bc = tc.borderContainer(title='In')
        top = bc.contentPane(region='top',height='50%', datapath='.record')
        bottom = bc.contentPane(region='center')
        fb = top.formbuilder(cols=2,border_spacing='4px')
        fb.field('account_name')
        fb.field('address')
        fb.field('full_name')
        fb.field('host')
        fb.field('port')
        #fb.field('protocol_code')
        fb.field('tls')
        fb.field('ssl')
        fb.field('username')
        fb.field('password')
        fb.field('last_uid')
        fb.button('check email', action='PUBLISH check_email')
        fb.dataRpc('dummy', self.db.table('email.message').receive_imap, subscribe_check_email=True, account='=.id')
        #self.account_messages(bottom)

        bottom.inlineTableHandler(relation='@account_users',viewResource=':ViewFromAccount',picker='user_id',title='!!Users')
        
        out = tc.contentPane(title='Out',datapath='.record')
        fb = out.div(padding='10px').formbuilder(cols=2,border_spacing='4px')
        fb.field('smtp_host')
        fb.field('smtp_from_address')
        fb.field('smtp_username')
        fb.field('smtp_password')
        fb.field('smtp_port')
        fb.field('smtp_tls')
        fb.field('smtp_ssl')
        fb.field('smtp_timeout')
        fb.field('system_bcc')

    def account_messages(self,bottom):
        th = bottom.dialogTableHandler(relation='@messages',
                                   dialog_height='600px',
                                   dialog_width='800px',
                                   dialog_title='Message')



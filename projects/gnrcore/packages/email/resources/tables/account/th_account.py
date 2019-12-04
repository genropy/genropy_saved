#!/usr/bin/python
# -*- coding: utf-8 -*-

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method


class View(BaseComponent):

    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('account_name',width='15em')
        r.fieldcell('address',width='20em')
        r.fieldcell('full_name',width='20em')
        r.fieldcell('host',width='20em')
        r.fieldcell('port',width='7em')
        r.fieldcell('protocol_code',width='10em')
        r.fieldcell('tls',width='7em')
        r.fieldcell('ssl',width='7em')
        r.fieldcell('last_uid',width='7em')
        r.fieldcell('schedulable',width='7em')

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
        tc = form.center.tabContainer(margin='2px')
        bc = tc.borderContainer(title='Input')
        top = bc.contentPane(region='top',datapath='.record')
        fb = top.div(padding='10px').formbuilder(cols=2,border_spacing='4px',
                                            fld_html_label=True)
        fb.field('account_name')
        fb.field('address')
        fb.field('full_name')
        fb.field('host')
        fb.field('port')
        #fb.field('protocol_code')
        fb.field('tls')
        fb.field('ssl')
        fb.field('username',type='password')
        fb.field('password')
        fb.field('last_uid')
        fb.field('schedulable')
        fb.button('check email', action='PUBLISH check_email')
        fb.dataRpc('dummy', self.db.table('email.message').receive_imap, subscribe_check_email=True, account='=.id')
        center = bc.contentPane(region='center')
        center.inlineTableHandler(relation='@account_users',
                                viewResource=':ViewFromAccount',
                                picker='user_id',title='!!Users',
                                pbl_classes=True,margin='2px')
        
        out = tc.contentPane(title='Output',datapath='.record')
        fb = out.div(padding='10px').formbuilder(cols=2,border_spacing='4px',
                        fld_html_label=True)
        fb.field('smtp_host')
        fb.field('smtp_from_address')
        fb.field('smtp_username')
        fb.field('smtp_password',type='password')
        fb.field('smtp_port')
        fb.field('smtp_tls')
        fb.field('smtp_ssl')
        fb.field('smtp_timeout')
        fb.field('system_bcc')
        fb.field('save_output_message',html_label=True)
        fb.field('send_limit')
        fb.field('debug_address')

    def account_messages(self,bottom):
        th = bottom.dialogTableHandler(relation='@messages',
                                   dialog_height='600px',
                                   dialog_width='800px',
                                   dialog_title='Message')
    
    def th_options(self):
        return dict(duplicate=True)



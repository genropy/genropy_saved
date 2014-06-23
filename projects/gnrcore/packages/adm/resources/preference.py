# -*- coding: UTF-8 -*-
#--------------------------------------------------------------------------
# Copyright (c) : 2004 - 2007 Softwell sas - Milano 
# Written by    : Giovanni Porcari, Michele Bertoldi
#                 Saverio Porcari, Francesco Porcari , Francesco Cavazzana
#--------------------------------------------------------------------------
#This library is free software; you can redistribute it and/or
#modify it under the terms of the GNU Lesser General Public
#License as published by the Free Software Foundation; either
#version 2.1 of the License, or (at your option) any later version.

#This library is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
#Lesser General Public License for more details.

#You should have received a copy of the GNU Lesser General Public
#License along with this library; if not, write to the Free Software
#Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA

class AppPref(object):
    def permission_adm(self, **kwargs):
        return 'admin'

    def prefpane_adm(self, parent, **kwargs):
        tc = parent.tabContainer(**kwargs)
        self._adm_general(tc.borderContainer(title='!!General', datapath='.general'))
        self._pr_instance_data(tc.contentPane(title='!!Instance data', datapath='.instance_data'))
        self._pr_mail(tc.contentPane(title='!!Mail options', datapath='.mail'))
        self._pr_backups(tc.contentPane(title='!!Backups', datapath='.backups'))


    def _adm_general(self, bc):
        top = bc.contentPane(region='top')
        fb = top.formbuilder(cols=1,border_spacing='3px')
        fb.numberTextBox(value='^.screenlock_timeout',lbl='!!Screenlock timeout (minutes)')
        fb.checkbox(value='^.forgot_password',label='Allow password recovery')
        fb.checkbox(value='^.new_user',label='New user registration')
        center = bc.tabContainer(region='center',margin='2px')
        self._auth_messages(center.contentPane(title='!!Authentication messages'))
        self._auth_email_confirm_template(center.borderContainer(title='!!Confirm user template'))
        self._auth_new_password_template(center.borderContainer(title='!!Confirm new password template'))

    def _auth_email_confirm_template(self,bc):
        bc.contentPane(region='top').formbuilder(cols=1,border_spacing='3px').textbox(value='^.confirm_user_subject',width='30em',lbl='!!Subject')
        bc.contentPane(region='center').simpleTextArea(value='^.confirm_user_tpl',editor=True)

    def _auth_new_password_template(self,bc):
        bc.contentPane(region='top').formbuilder(cols=1,border_spacing='3px').textbox(value='^.confirm_password_subject',width='30em',lbl='!!Subject')
        bc.contentPane(region='center').simpleTextArea(value='^.confirm_password_tpl',editor=True)


    def _auth_messages(self,pane):
        fb = pane.formbuilder(cols=1,border_spacing='3px')
        fb.textbox(value='^.login_title',width='30em',lbl='Login title',)
        fb.textbox(value='^.new_window_title',width='30em',lbl='New window title')
        fb.textbox(value='^.lost_password',width='30em',lbl='!!Lost password')
        fb.textbox(value='^.new_password',width='30em',lbl='New password')
        fb.textbox(value='^.check_email',width='30em',lbl='Check email')
        fb.textbox(value='^.confirm_user_title',width='30em',lbl='Confirm user title')
        fb.textbox(value='^.confirm_user_message',width='30em',lbl='Confirm user message')
        fb.textbox(value='^.new_user_ok_message',width='30em',lbl='New user ok message')



    def _pr_backups(self, pane):
        fb = pane.div(padding='5px').formbuilder(cols=1, border_spacing='3px')
        fb.textbox(value='^.backup_folder',lbl='Folder path')
        fb.numberTextBox(value='^.max_copies',lbl='Max copies')

    def _pr_mail(self, pane):
        fb = pane.div(margin='5px').formbuilder(cols=1, border_spacing='6px', width='100%', fld_width='100%',
                                                    tdl_width='10em')
        if 'email' in self.db.packages:
            fb.dbselect(value='^.email_account_id',lbl='Account',dbtable='email.account',hasDownArrow=True)
        
        fb.div(lbl='Mail Settings', colspan=2, lbl_font_style='italic', lbl_margin_top='1em', margin_top='1em',
               lbl_color='#7e5849',disabled='^.email_account_id')
        fb.textbox(value='^.smtp_host', lbl='SMTP Host', dtype='T',disabled='^.email_account_id')
        fb.textbox(value='^.from_address', lbl='From address', dtype='T',disabled='^.email_account_id')
        fb.textbox(value='^.user', lbl='Username', dtype='T',disabled='^.email_account_id')
        fb.textbox(value='^.password', lbl='Password', disabled='^.email_account_id', type='password')
        fb.textbox(value='^.port', lbl='Port', disabled='^.email_account_id')
        fb.checkbox(value='^.tls', lbl='TLS', dtype='B', disabled='^.email_account_id')
        fb.checkbox(value='^.ssl', lbl='SSL', dtype='B', disabled='^.email_account_id')
        fb.textbox(value='^.system_bcc', lbl='System bcc',disabled='^.email_account_id')


    def _pr_instance_data(self, pane):
        fb = pane.div(margin='5px').formbuilder(cols=1, border_spacing='6px', width='100%', fld_width='100%',
                                                tdl_width='10em')
        fb.textbox(value='^.owner_name', lbl='!!Owner name')
        fb.textbox(value='^.logo_url', lbl='Logo url')
        fb.img(url='^.logo_url')


class UserPref(object):
    def prefpane_adm(self, parent, **kwargs):
        tc = parent.tabContainer(**kwargs)
        self._adm_general(tc.contentPane(title='!!General options', datapath='.general'))

        self._adm_mail(tc.contentPane(title='!!Mail options', datapath='.mail'))

    def _adm_general(self, pane):
        fb = pane.formbuilder(cols=1,border_spacing='3px',margin='10px')
        fb.numberTextBox(value='^.screenlock_timeout',lbl='!!Screenlock timeout (minutes)')

    def _adm_mail(self, pane):
        fb = pane.div(margin='5px').formbuilder(cols=1, border_spacing='6px', width='100%', fld_width='100%')
        if 'email' in self.db.packages:
            fb.dbselect(value='^.email_account_id',lbl='Account',dbtable='email.account',hasDownArrow=True)
        fb.div(lbl='Mail Settings', colspan=2, lbl_font_style='italic', lbl_margin_top='1em', margin_top='1em',
               lbl_color='#7e5849')
        fb.textbox(value='^.smtp_host', lbl='SMTP Host', dtype='T', disabled='^.email_account_id')
        fb.textbox(value='^.from_address', lbl='From address', dtype='T', disabled='^.email_account_id')
        fb.textbox(value='^.user', lbl='Username', dtype='T', disabled='^.email_account_id')
        fb.textbox(value='^.password', lbl='Password', dtype='T', disabled='^.email_account_id', type='password')
        fb.textbox(value='^.port', lbl='Port', dtype='T', disabled='^.email_account_id')
        fb.checkbox(value='^.tls', lbl='TLS', dtype='B', disabled='^.email_account_id')
            
        
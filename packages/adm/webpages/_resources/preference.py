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
    def permission_adm(self,**kwargs):
        return 'admin'

    def prefpane_adm(self,parent,**kwargs):
        tc = parent.tabContainer(**kwargs)

        self._pr_mail(tc.contentPane(title='!!Mail options',datapath='.mail'))
        self._pr_logo(tc.contentPane(title='!!Logo',datapath='.logo'))
    
    def _pr_mail(self,pane):
        fb = pane.div(margin='5px').formbuilder(cols=1, border_spacing='6px',width='100%',fld_width='100%')
        fb.div(lbl='Mail Settings', colspan=2, lbl_font_style='italic', lbl_margin_top='1em', margin_top='1em',lbl_color='#7e5849')
        fb.textbox(value='^.smtp_host',lbl='SMTP Host',dtype='T', colspan=1)
        fb.textbox(value='^.from_address',lbl='From address',dtype='T', colspan=1)
        fb.textbox(value='^.user',lbl='Username',dtype='T', colspan=1)
        fb.textbox(value='^.password',lbl='Password',dtype='T', colspan=1, type='password')
        fb.textbox(value='^.port',lbl='Port', dtype='T', colspan=1)
        fb.checkbox(value='^.tls',lbl='TLS',dtype='B', colspan=1)
        
    def _pr_logo(self,pane):
        pass

class UserPref(object):
    def prefpane_adm(self,parent,**kwargs):
        tc = parent.tabContainer(**kwargs)
        self._pr_mail(tc.contentPane(title='!!Mail options',datapath='.mail'))
    
    def _pr_mail(self,pane):
        fb = pane.div(margin='5px').formbuilder(cols=1, border_spacing='6px',width='100%',fld_width='100%')
        fb.div(lbl='Mail Settings', colspan=2, lbl_font_style='italic', lbl_margin_top='1em', margin_top='1em',lbl_color='#7e5849')
        fb.textbox(value='^.smtp_host',lbl='SMTP Host',dtype='T', colspan=1)
        fb.textbox(value='^.from_address',lbl='From address',dtype='T', colspan=1)
        fb.textbox(value='^.user',lbl='Username',dtype='T', colspan=1)
        fb.textbox(value='^.password',lbl='Password',dtype='T', colspan=1, type='password')
        fb.textbox(value='^.port',lbl='Port', dtype='T', colspan=1)
        fb.checkbox(value='^.tls',lbl='TLS',dtype='B', colspan=1)
        
        
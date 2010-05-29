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
        fb = pane.formbuilder(cols=1, border_spacing='6px')
        fb.textbox(value='^.host',lbl='!!Host')
        fb.checkbox(value='^.ssl',label='!!Use SSL')
        
    def _pr_logo(self,pane):
        pass

class UserPref(object):
    def prefpane_adm(self,parent,**kwargs):
        tc = parent.tabContainer(**kwargs)
        self._pr_mail(tc.contentPane(title='!!Mail options',datapath='.mail'))
    
    def _pr_mail(self,pane):
        fb = pane.formbuilder(cols=1, border_spacing='6px')
        fb.textbox(value='^.user',lbl='!!User')
        fb.checkbox(value='^.password',label='!!Password')
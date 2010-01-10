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

"""
Component for thermo:
"""
from gnr.web.gnrwebpage import BaseComponent

class SiteLayout(BaseComponent):
    css_requires='genropynet'

    def site_header(self,header):
        header.span('menu')
        loginbox = header.div(float='right',margin_right='10px')
        if self.user:
            self.site_login_logged(loginbox) 
        else:
            self.site_login_unlogged(loginbox)
            
    def site_login_logged(self,box):
        pass
    def site_login_unlogged(self,box):
        fb = box.formbuilder(cols=3,border_spacing='4px',_class='loginfb',
                            datapath='login',onEnter='FIRE .enter')
        fb.textbox(value='^.user',ghost='User',_autoselect=True,width='10em')
        fb.textbox(value='^.password',ghost='Password',lbl_width='1em',type='password',
                 width='10em',_autoselect=True)
        fb.button('Enter',baseClass='loginbutton',fire='.enter')
        fb.dataRpc('_aux.login', 'doLogin', login='=login', btn='^.enter',_onResult='FIRE afterLogin')
        fb.dataScript('_aux.dologin',"genro.gotoURL('startpage')" , message='=_aux.login.message',
                                _if="message==''", _else="FIRE error_msg = badUserMsg; SET _aux.login = null;",
                             badUserMsg="!!Incorrect Login",_fired='^afterLogin')   
        fb.div('^error_msg',nodeId='bottomMsg',colspan=2,text_align='center',_class='disclaimer')
        fb.dataController("genro.dom.effect('bottomMsg','fadeout',{duration:3000,delay:3000});", 
                          msg='^error_msg',_if='msg')
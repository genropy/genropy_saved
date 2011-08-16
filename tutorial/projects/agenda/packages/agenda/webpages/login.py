# -*- coding: UTF-8 -*-

# login.py
# Created by Filippo Astolfi on 2011-03-03.
# Copyright (c) 2011 Softwell. All rights reserved.

from gnr.web.gnrwebstruct import struct_method

class GnrCustomWebPage(object):
    py_requires = "login_component"
    
    def main(self, root, **kwargs):
        self.rootAttributes(root.attributes)
        root.loginFrame(title='!!Agenda Login',shadow='2px 2px 2px gray',rounded=12,
                        gradient_from='orange',gradient_to='white',gradient_deg=90,**kwargs)
                        
    @struct_method
    def loginCenter(self,frame):
        fb = frame.formbuilder(border_spacing='3px',onEnter='PUBLISH login;',margin='auto',
                               margin_top='15px',fld_line_height='20px',fld_padding='2px',fld_rounded=6)
        fb.textbox(value='^.user',ghost='Username: agenda')
        fb.textbox(value='^.password',ghost='Password: guest',type='password')
        frame.button('Entra',action='PUBLISH login;',padding='1px',rounded=10,bottom='3px',right='32px',position='absolute')
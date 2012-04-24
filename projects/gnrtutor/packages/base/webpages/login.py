#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-

"""
  login

  Created by Giovanni Porcari on 2007-03-24.
  Copyright (c) 2007 Softwell. All rights reserved.
"""


# --------------------------- GnrWebPage subclass ---------------------------
class GnrCustomWebPage(object):
    css_requires = 'public'
    def rootWidget(self, root, **kwargs):
        return root.framePane(_class='loginbox',margin='auto',width='360px',height='240px', **kwargs)

    def mainLeftContent(self,*args,**kwargs):
        pass

    def main(self, frame, fromPage=None, **kwargs):
        frame.bottom.slotBar('*,messageBox,*',messageBox_subscribeTo='invalid_login',messageBox_color='gray',messageBox_font_size='16px',height='25px')

        fb = frame.formbuilder(cols=2, onEnter="FIRE do_login=true",border_spacing='7px',margin='auto',margin_top='45px') 
        fb.div('Enter your username \'demo\' and password \'demo\'',colspan=2)
        fb.div('',colspan=2)

        fb.textbox(ghost='User', value='^form.user', width='20em',autofocus=True, background_color='#FFFFFF',
                   _class='loginInput',colspan=2, _autoselect=True )
                                                                     
        fb.textbox(ghost='Password', type='password', value='^form.password', background_color='#FFFFFF',
                   _class='loginInput',width='20em',colspan=2, _autoselect=True) # placeholder


        frame.button('LOGIN',fire='do_login',width='10em',font_size='15px',line_height='22px',#baseClass='loginbox',
                             position='absolute',bottom='30px',right='50px') # _class='base' ?,label_color='#a1a1a1'

        frame.dataController("genro.login(data)",_fired="^do_login",data='=form')

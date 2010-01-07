#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  untitled
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#

""" login.py """

from gnr.core.gnrbag import Bag

class GnrCustomWebPage(object):
    py_requires = 'public:Public'
    def rootWidget(self, root, **kwargs):
        return root.borderContainer(_class='loginbox',margin='auto', **kwargs)
    
    def main(self, rootbc, fromPage=None, **kwargs):
        self.controller(rootbc, fromPage)
        bottom = rootbc.borderContainer(region='bottom',height='30px',_class='msgbox')
        self.pbl_bottomBar(bottom)

        client = rootbc.contentPane(region='center')
        fb = client.formbuilder(cols=2,onEnter="FIRE loginbtn=true",border_spacing='15px',margin='auto',margin_top='20px') 
        fb.div('Login',_class='formTitle',colspan=2)
        fb.textbox(value='^form.user', autofocus=True, width='20em',default_value='Username',
                   _class='loginInput',colspan=2, _autoselect=True)
        fb.textbox(type='password',default_value='Password', value='^form.password', _class='loginInput',width='20em',colspan=2, _autoselect=True)
        btn = fb.div(_class='loginbtn',float='right',connect_onclick='FIRE loginbtn')
        newUserUrl = self.application.newUserUrl()
        if newUserUrl:
            newUserUrl = self.getDomainUrl(newUserUrl)  
            bottom['left'].div('!!Register', connect_onclick="genro.gotoURL('%s')" % newUserUrl, _class='bottom_btn',float='left')
        
    def controller(self, root, fromPage):
        root.data('fromPage', fromPage)
        root.dataRpc('_aux.login', 'doLogin', login='=form', btn='^loginbtn')
        if fromPage:
            root.dataScript('_aux.dologin',"genro.gotoURL(fromPage)" , fromPage='=fromPage' , message='^_aux.login.message',
                                _if="message==''", _else="FIRE pbl.bottomMsg = badUserMsg;SET _aux.login = null;", badUserMsg="!!Incorrect Login")
        else:
            root.dataScript('_aux.dologin',"genro.gotoHome()" , message='^_aux.login.message',
                                _if="message==''", _else="FIRE pbl.bottomMsg = badUserMsg;SET _aux.login = null;", badUserMsg="!!Incorrect Login")
        
        
        

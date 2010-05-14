#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  login
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#

""" login.py """

class GnrCustomWebPage(object):
    py_requires = 'public:Public'

    def rootWidget(self, root, **kwargs):
        return root.borderContainer(_class='smallbox',**kwargs)
                      
    def pbl_topBar(self,top,title=None,flagsLocale=False):
        """docstring for publicTitleBar"""
        pass

    def pbl_bottomLeft(self,pane):
        pass
            
    def mainLeftContent(self,*args,**kwargs):
        pass
            
    def main(self, root, fromPage=None, **kwargs):
        self.controller(root, fromPage)
        pane, top, bottom = self.pbl_rootContentPane(root,flagsLocale=False,**kwargs)
        
        fb = pane.formbuilder(cols=2,onEnter="FIRE loginbtn=true",margin='auto',margin_top='5ex',border_spacing='10px') 
        fb.textbox(value='^form.user',width='20em',ghost='User',colspan=2,autofocus=True,_autoselect=True)
        fb.textbox(ghost= 'Password',type='password', value='^form.password',width='20em',colspan=2,_autoselect=True)
        fb.button('!!Enter',baseClass='baseButton',float='right',fire='loginbtn',colspan=2)
        
    def controller(self, root, fromPage):
        root.data('fromPage', fromPage)
        root.dataRpc('_aux.login', 'doLogin', login='=form', btn='^loginbtn')
        if fromPage:
            root.dataScript('_aux.dologin',"genro.gotoURL(fromPage)" , fromPage='=fromPage' , message='^_aux.login.message',
                            _if="message==''", _else="FIRE pbl.bottomMsg = badUserMsg;SET _aux.login = null;",
                             badUserMsg="!!Access Denied")
        else:
            root.dataScript('_aux.dologin',"genro.gotoHome()" , message='^_aux.login.message',
                                _if="message==''", _else="FIRE pbl.bottomMsg = badUserMsg;SET _aux.login = null;",
                             badUserMsg="!!Access Denied")


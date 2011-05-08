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

    def main(self, root, fromPage=None, **kwargs):
        self.controller(root, fromPage)
        #root = root.contentPane(region='center')
        client, top, bottom = self.pbl_rootContentPane(root, '!!Login', width='25em', height='25ex', centered=True)
        fb = client.formbuilder(cols=1, onEnter="FIRE loginbtn=true", border_spacing='8px', margin='auto',
                                margin_top='1ex')
        fb.textbox(lbl='!!User', value='^form.user', autofocus=True, width='16em',
                   _autoselect=True) # TODO autoFocus or _autoselect sometime cause a "this.focus -- focus is unassigned" error in JS on Firefox
        fb.textbox(lbl='!!Password', type='password', value='^form.password', width='16em', _autoselect=True)
        newUserUrl = self.application.newUserUrl()
        if newUserUrl:
            newUserUrl = self.getDomainUrl(newUserUrl)
            fb.a('!!Register', href=newUserUrl)
        fb.a('!!Password lost?', href='lost_password')
        bottom['right'].button('!!Login', fire='loginbtn', float='right', baseClass='bottom_btn', margin='1px')
        bottom['left'].button('!!Cancel', action='genro.pageBack()', float='left', baseClass='bottom_btn', margin='1px')

    def pbl_topBar(self, top, title=None, flagsLocale=False):
        """redefinition of the topbar for the login"""
        left = top.contentPane(region='left', width='25%')
        self.pbl_topBarLeft(left)
        right = top.contentPane(region='right', width='25%', padding_top='5px', padding_right='8px')
        right.div(connect_onclick='genro.pageBack()', _class='goback', tooltip='!!Torna alla pagina precedente')
        center = top.contentPane(region='center', margin_top='3px')
        if title:
            center.div(title, _class='pbl_title_caption')
        right.dataRpc('aux.locale_ok', 'changeLocale', locale='^aux.locale')
        right.dataScript('dummy', 'genro.pageReload()', fired='^aux.locale_ok')
        #right.div(connect_onclick="genro.pageBack()", tooltip="!!Back",
        #          _class='icnBaseUpYellow buttonIcon', content='&nbsp;', float='right',margin_left='10px')
        if self.user:
            right.div(connect_onclick="genro.logout()", tooltip="!!Logout",
                      _class='icnBaseLogout buttonIcon', content='&nbsp;', float='right')
            right.div(content=self.user, float='right', _class='pbl_username buttonIcon')

        return center

    def controller(self, root, fromPage):
        root.data('fromPage', fromPage)
        root.dataRpc('_aux.login', 'doLogin', login='=form', btn='^loginbtn')
        if fromPage:
            root.dataScript('_aux.dologin', "genro.gotoURL(fromPage)", fromPage='=fromPage',
                            message='^_aux.login.message',
                            _if="message==''", _else="FIRE pbl.bottomMsg = badUserMsg;SET _aux.login = null;",
                            badUserMsg="!!User unknown or wrong password")
        else:
            root.dataScript('_aux.dologin', "genro.gotoHome()", message='^_aux.login.message',
                            _if="message==''", _else="FIRE pbl.bottomMsg = badUserMsg;SET _aux.login = null;",
                            badUserMsg="!!User unknown or wrong password")
        
        
        

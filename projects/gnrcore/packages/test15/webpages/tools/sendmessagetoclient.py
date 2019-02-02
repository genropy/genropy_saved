# -*- coding: utf-8 -*-

# dataremote.py
# Created by Francesco Porcari on 2010-10-29.
# Copyright (c) 2010 Softwell. All rights reserved.

"""dataRemote"""

from builtins import object
class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerFull,gnrcomponents/chat_component/chat_component:ChatComponent"
    
    def test_1_basic(self, pane):
        """Sendmessage"""
        pane.textbox(value='^.message',lbl='Message')
        pane.textbox(value='^.user',lbl='User')
        pane.button('Send',action='FIRE .sendmessage')
        pane.dataRpc('dummy',self.chatMessageToUser,
                    msg='=.message', #roomId=None, 
                    user='=.user', #disconnect=False, 
                   sysmessage=True,
                    _fired='^.sendmessage')




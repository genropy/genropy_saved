# -*- coding: UTF-8 -*-

# dataremote.py
# Created by Francesco Porcari on 2010-10-29.
# Copyright (c) 2010 Softwell. All rights reserved.

"""dataRemote"""

from gnr.core.gnrdecorator import public_method
from gnr.core.gnrbag import Bag
from datetime import datetime
class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerFull,gnrcomponents/chat_component/chat_component:ChatComponent"
    
    def test_1_basic(self, pane):
        """Sendmessage"""
        pane.textbox(value='^.message',lbl='Message')
        pane.textbox(value='^.from_user',lbl='From User')
        pane.textbox(value='^.user',lbl='User')
        pane.button('Send',action='FIRE .sendmessage')
        pane.dataRpc('dummy',self.sendMessageToChat,
                    msg='=.message', #roomId=None, 
                    user='=.user', #disconnect=False, 
                    from_user='=.from_user',
                    priority=None,
                    _fired='^.sendmessage')


    @public_method
    def sendMessageToChat(self,msg=None,user=None,from_user=None,roomId=None,priority=None,disconnect=None,users=None):
        from_user = from_user or  self.user
        roomId = roomId or 'cr_system_message'
        path = 'gnr.chat.msg.%s' % roomId
        priority = priority or 'H'
        if not users:
            users = Bag()
            if from_user!='SYSTEM':
                users.setItem(from_user,None,user_name=from_user,user=from_user)
            users.setItem(user,None,user_name=user,user=user)
        ts = self.toText(datetime.now(), format='HH:mm:ss')
        with self.userStore(user) as store:
            if disconnect and (user == from_user):
                store.drop_datachanges(path)
            else:
                in_out = 'in' if user != from_user else 'out'
                value = Bag(dict(msg=msg, roomId=roomId, users=users, roomtitle='System messages',from_user=from_user,
                                 in_out=in_out, ts=ts, disconnect=disconnect))
                store.set_datachange(path, value, fired=True, reason='chat_out')
        self.setInClientData(path='gnr.chat.room_alert', value=Bag(dict(roomId=roomId, users=users, priority=priority,roomtitle='System piero')),
                                     filters='user:%s' % user, fired=True, reason='chat_open',
                                     public=True, replace=True)#



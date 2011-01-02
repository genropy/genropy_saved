# -*- coding: UTF-8 -*-

# user_store.py
# Created by Francesco Porcari on 2010-09-08.
# Copyright (c) 2010 Softwell. All rights reserved.

from datetime import datetime

class GnrCustomWebPage(object):
    "User store"
    py_requires = "gnrcomponents/testhandler:TestHandlerFull"

    def pageAuthTags(self, method=None, **kwargs):
        return 'user'

    def test_1_send(self, pane):
        bc = pane.borderContainer(height='250px', datapath='test1')
        right = bc.contentPane(region='right', width='40%')
        center = bc.contentPane(region='center')
        fb = center.formbuilder(cols=1, border_spacing='3px')
        fb.textbox(value='^.user', lbl='Talk to')
        fb.div(nodeId='chat_monitor', height='150px', overflow='auto',
               width='20em', background='white', border='1px solid gray')
        fb.dataController("SET rows_datapath = 'gnr._chat.rooms.'+user;", user='^.user')
        fb.dataController("""
                            var rootnode= genro.nodeById("chat_monitor");
                            var domNode = rootnode.domNode;
                            rootnode.clearValue().freeze();
                            rows.forEach(function(n){
                                var attr = n.attr;
                                var msgattr = {};
                                msgattr['float'] = attr['in_out']=='out'?'left':'right';
                                msgattr['color'] = attr['in_out']=='out'?'red':'green';
                                msgattr.content = n.getValue();
                                var line = rootnode._('div',{height:lineHeight+'px'});
                                line._('div',msgattr);
                            });
                            rootnode.unfreeze();
                            var scrollHeight = genro.nodeById("chat_monitor").domNode.scrollHeight;
                            var scrollTop;
                            if (scrollHeight>boxHeight){
                                scrollTop = scrollHeight-domNode.scrollWidth;
                            }
                            if (scrollTop){
                                rootnode.domNode.scrollTop = scrollTop;
                            }
                            
                            """, rows="^.rows", datapath='^rows_datapath', _if='rows', lineHeight=20,
                          boxHeight=150)
        fb.textbox(value='^.message', lbl='Msg')
        fb.button('send', fire='.send')
        center.dataRpc('dummy', 'send_message', user='=.user', msg='=.message', _fired='^.send', _if='user&&msg')

    def rpc_send_message(self, user=None, msg=None):
        ts = datetime.now()
        path = 'gnr._chat.rooms.%s.rows.#id'
        with self.userStore(self.user) as store:
            store.set_datachange(path % user, msg, fired=False, reason='chat_in',
                                 attributes=dict(from_user=self.user, in_out='out', ts=ts))
        with self.userStore(user) as store:
            store.set_datachange(path % self.user, msg, fired=False, reason='chat_out',
                                 attributes=dict(from_user=self.user, in_out='in', ts=ts))
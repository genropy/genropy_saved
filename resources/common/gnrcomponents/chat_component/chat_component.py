# -*- coding: UTF-8 -*-

# chat_component.py
# Created by Francesco Porcari on 2010-09-08.
# Copyright (c) 2011 Softwell. All rights reserved.

from gnr.web.gnrwebpage import BaseComponent
from gnr.core.gnrbag import Bag
from datetime import datetime
from gnr.core.gnrdecorator import public_method

class ChatComponent(BaseComponent):
    py_requires = 'foundation/includedview:IncludedView'
    css_requires = 'gnrcomponents/chat_component/chat_component'
    js_requires = 'gnrcomponents/chat_component/chat_component'

    def mainLeft_chat_plugin(self, pane):
        """!!Chat"""
        frame = pane.framePane(frameCode='ct_chatmain',datapath='gnr.chat')
        bar = frame.top.slotToolbar('5,ctitle,*,userselect')
        bar.ctitle.div('!!Chat',font_size='.9em')
        self.ct_chat_grid(bar.userselect.div(_class='iconbox man',tip='!!Connected users'))
        self.ct_chat_form(frame)


    def ct_controller_main(self, pane):
        pane.dataRpc('dummy', 'setStoreSubscription', subscribe_chat_plugin_on=True,
                     storename='user', client_path='gnr.chat.msg', active=True,
                    _onResult='genro.rpc.setPolling(2,2);')
        pane.dataRpc('dummy', 'setStoreSubscription', active=False, subscribe_chat_plugin_off=True, storename='user',
                    _onCalling='genro.rpc.setPolling();')

        pane.dataController("""genro.playSound('NewMessage'); 
                                setTimeout(function(){
                                    genro.dom.setClass(dojo.body(),'newMessage',true);

                                },1)
                            """,
                            roomId="^gnr.chat.room_alert", selectedTab='=#gnr_main_left_center.selected',
                            sel_room='=gnr.chat.selected_room',rooms='=gnr.chat.rooms')
        pane.dataController("""
                              var unread = rooms.sum('unread');
                              genro.dom.setClass(dojo.body(),'newMessage',unread>0);
                              """, rooms='=gnr.chat.rooms', _fired='^gnr.chat.calc_unread')


    def ct_chat_form(self, frame):
        self.ct_controller_main(frame)

        frame.dataController("ct_chat_utils.read_msg(_node.getValue());", msgbag="^gnr.chat.msg")

        frame.center.tabContainer(nodeId='ct_chat_rooms', margin='5px', _class='chat_rooms_tab',
                        selectedPage='^.selected_room')
        frame.dataController("""
                             var roombag = rooms.getItem(sel_room);
                             roombag.setItem('unread',null);
                             FIRE gnr.chat.calc_unread;
                             ct_chat_utils.fill_title(roombag);
                            """, sel_room='^.selected_room', rooms='=.rooms')
        frame.dataRpc('dummy', self.ct_send_message, subscribe_ct_send_message=True,
                    _onCalling="""
                                var roombag =this.getRelativeData("gnr.chat.rooms."+kwargs.roomId);
                                var msg = kwargs.msg || roombag.getItem('current_msg');
                                if (!msg && !kwargs.disconnect){
                                    return false;
                                }
                                kwargs.msg=msg
                                kwargs.users=roombag.getItem('users');
                                roombag.setItem('current_msg','');
                                """,
                    _onResult="""
                                var textbox = dojo.byId("ct_msgtextbox_"+kwargs.roomId);
                                if(textbox){textbox.focus();}
                                """)

    def ct_chat_grid(self, button):
        tp = button.tooltipPane(onOpening="""genro.getDataNode('gnr.chat.connected_users.#0');
                                                setTimeout(function(){
                                                    genro.getFrameNode('ct_connected_user').widget.resize()
                                                },1)
                                                """)
        frame = tp.framePane(frameCode='ct_connected_user',height='400px',width='230px',_class='noheader')

        frame.data('.grid_users', Bag())
        frame.dataRemote('gnr.chat.connected_users', 'connection.connected_users_bag',cacheTime=2)

        def struct(struct):
            r = struct.view().rows()
            r.cell('user_name', dtype='T', name='Fullname', width='16em')

        bar = frame.top.slotToolbar('5,vtitle,*,searchOn',font_size='.8em')
        bottom = frame.bottom.slotBar('*,openchat,2',font_size='.9em',padding='2px',border_top='1px solid silver')
        bottom.openchat.button('!!Add and close',action='FIRE #ct_connected_user_grid.open_chat; tp.widget.onCancel();',tp=tp,
                                disabled='^#ct_connected_user_grid.selectedIndex?=(#v==null)')
        bar.vtitle.div('!!Users')
        frame.includedview(identifier='user',
                           datapath='.grid_users',
                           selectedIndex='.selectedIndex',
                           storepath='gnr.chat.connected_users',
                           label='!!Users',
                         connect_onRowDblClick="""FIRE .open_chat;""",
                         struct=struct)

        frame.dataController("""SET gnr.chat.curr_address = 'gnr.chat.rooms.'+user;
                               """, user='^#ct_connected_user_grid.selectedId',
                          _if='user', _else='SET gnr.chat.disabled=true;')
        frame.dataController("""
                            var grid = genro.wdgById(gridId);
                            var rows = grid.getSelectedNodes();
                            var users =new gnr.GnrBag();
                            dojo.forEach(rows,function(n){
                                users.setItem(n.attr.user,null,{user_name:n.attr.user_name,user:n.attr.user});
                            });
                            var roomId= 'cr_'+new Date().getTime();
                            ct_chat_utils.open_chat(roomId,users);
                            """,
                            _fired="^#ct_connected_user_grid.open_chat",
                            gridId='ct_connected_user_grid')

    @public_method
    def ct_send_message(self, msg=None, roomId=None, users=None, disconnect=False):
        ts = self.toText(datetime.now(), format='HH:mm:ss')
        if disconnect:
            msg = '<i>User %s left the room</i>' % self.user
        path = 'gnr.chat.msg.%s' % roomId
        for userNode in users:
            user = userNode.label
            with self.userStore(user) as store:
                if disconnect and (user == self.user):
                    store.drop_datachanges(path)
                else:
                    in_out = 'in' if user != self.user else 'out'
                    value = Bag(dict(msg=msg, roomId=roomId, users=users, from_user=self.user,
                                     in_out=in_out, ts=ts, disconnect=disconnect))
                    store.set_datachange(path, value, fired=True, reason='chat_out')
            if user != self.user:
                self.setInClientData(path='gnr.chat.room_alert', value=Bag(dict(roomId=roomId, users=users)),
                                     filters='user:%s' % user, fired=True, reason='chat_open',
                                     public=True, replace=True)

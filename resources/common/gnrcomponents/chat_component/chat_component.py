# -*- coding: UTF-8 -*-

# chat_component.py
# Created by Francesco Porcari on 2010-09-08.
# Copyright (c) 2010 Softwell. All rights reserved.

from gnr.web.gnrwebpage import BaseComponent
from gnr.core.gnrbag import Bag
from datetime import datetime

class ChatComponent(BaseComponent):
    py_requires = 'foundation/includedview:IncludedView'
    css_requires = 'gnrcomponents/chat_component/chat_component'
    js_requires = 'gnrcomponents/chat_component/chat_component'

    def mainLeft_chat_plugin(self, pane):
        """!!Chat"""
        self.ct_chat_main(pane.borderContainer())

    def ct_chat_main(self, bc):
        toolbar = bc.contentPane(region='top').toolbar()
        ttdialog = toolbar.dropDownButton(label='User').tooltipDialog(title='!!Users list', datapath='gnr.chat',
                                                                      nodeId='ct_chat_list_users_dlg',
                                                                      connect_onOpen='genro.wdgById("ct_chat_list_users").resize(); FIRE .listusers;'
                                                                      ).borderContainer(height='300px', width='250px',
                                                                                        nodeId='ct_chat_list_users')
        self.ct_chat_grid(ttdialog)
        self.ct_chat_form(bc.borderContainer(region='center', datapath='gnr.chat', margin='3px'))

    def ct_controller_main(self, pane):
        pane.dataRpc('dummy', 'setStoreSubscription', subscribe_chat_plugin_on=True,
                     storename='user', client_path='gnr.chat.msg', active=True,
                     _onResult='genro.rpc.setPolling(2,2);')
        pane.dataRpc('dummy', 'setStoreSubscription', active=False, subscribe_chat_plugin_off=True, storename='user',
                     _onCalling='genro.rpc.setPolling();')

        pane.dataController("genro.playSound('NewMessage');",
                            roomId="^gnr.chat.room_alert", selectedTab='=#gnr_main_left_center.selected',
                            sel_room='=gnr.chat.selected_room')
        pane.dataController("""
                              var unread = rooms.sum('unread');
                              genro.dom.setClass(dojo.body(),'newMessage',unread>0);
                              """, rooms='=gnr.chat.rooms', _fired='^gnr.chat.calc_unread')


    def ct_chat_form(self, bc):
        self.ct_controller_main(bc)

        bc.dataController("""SET gnr.chat.curr_address = 'gnr.chat.rooms.'+user;
                               """, user='^#ct_connected_user_grid.selectedId',
                          _if='user', _else='SET gnr.chat.disabled=true;')
        bc.dataController("""
                            var grid = genro.wdgById(gridId);
                            var rows = grid.getSelectedNodes();
                            var users =new gnr.GnrBag();
                            dojo.forEach(rows,function(n){users.setItem(n.attr.user,null,{user_name:n.attr.user_name,user:n.attr.user})});
                            var roomId= 'cr_'+new Date().getTime();
                            ct_chat_utils.open_chat(roomId,users);
                            """,
                          _fired="^#ct_connected_user_grid.open_chat",
                          gridId='ct_connected_user_grid')

        bc.dataController("ct_chat_utils.read_msg(_node.getValue());", msgbag="^gnr.chat.msg")

        bc.tabContainer(region='center', nodeId='ct_chat_rooms', margin='5px', _class='chat_rooms_tab',
                        selectedPage='^.selected_room')
        bc.dataController("""
                             var roombag = rooms.getItem(sel_room);
                             roombag.setItem('unread',null);
                             FIRE gnr.chat.calc_unread;
                             ct_chat_utils.fill_title(roombag);
                            """, sel_room='^.selected_room', rooms='=.rooms')
        bc.dataRpc('dummy', 'ct_send_message', subscribe_ct_send_message=True,
                   _onCalling="""
                                var roombag =this.getRelativeData("gnr.chat.rooms."+kwargs.roomId);
                                var msg = roombag.getItem('current_msg');
                                if (!msg && !kwargs.disconnect){
                                    return false;
                                }
                                kwargs.users=roombag.getItem('users');
                                kwargs.msg=msg
                                roombag.setItem('current_msg','');
                                """,
                   _onResult="""
                                var textbox = dojo.byId("ct_msgtextbox_"+kwargs.roomId);
                                if(textbox){textbox.focus();}
                                """)

    def ct_chat_grid(self, bc):
        bc.data('.grid_users', Bag())
        bc.dataRpc('.connected_users', 'connection.connected_users_bag', _fired='^.listusers')

        def struct(struct):
            r = struct.view().rows()
            r.cell('user_name', dtype='T', name='Fullname', width='16em')
            return struct

        def footer(pane):
            pane.button('Confirm', action='FIRE .open_chat;genro.wdgById("ct_chat_list_users_dlg").onCancel();')

        self.includedViewBox(bc, nodeId='ct_connected_user_grid',
                             identifier='user',
                             datapath='.grid_users', filterOn='!!Search:user_name',
                             storepath='gnr.chat.connected_users',
                             footer=footer,
                             label='!!Users',
                             connect_onRowDblClick="""
                                                    FIRE .open_chat;
                                                    genro.wdgById("ct_chat_list_users_dlg").onCancel();
                                                    """,
                             struct=struct, autoWidth=True)


    def rpc_ct_send_message(self, msg=None, roomId=None, users=None, disconnect=False):
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

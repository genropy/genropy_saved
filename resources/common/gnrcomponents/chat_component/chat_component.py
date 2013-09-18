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

    def btn_chat_plugin(self,pane,**kwargs):
        """CALLED BY FRAMEDINDEX"""
        pane.div(_class='button_block iframetab').div(_class='chat_plugin_icon',tip='!!Chat plug-in',
                    connect_onclick="""PUBLISH open_plugin = "chat_plugin";""",
                    nodeId='plugin_block_chat_plugin')
    

    def ct_controller_main(self, pane):
        pane.dataRpc('dummy', 'setStoreSubscription', subscribe_chat_plugin_on=True,
                     storename='user', client_path='gnr.chat.msg', active=True,
                    _onResult='genro.setFastPolling(true);')
        pane.dataRpc('dummy', 'setStoreSubscription', active=False, client_path='gnr.chat.msg',
                    subscribe_chat_plugin_off=True, storename='user',_onCalling='genro.setFastPolling(false);')

        pane.dataController(""" var roomId = pars.getItem('roomId');
                                var priority = pars.getItem('priority');
                                console.log(roomId,priority);
                                if (priority=='H'){
                                    PUBLISH open_plugin = "chat_plugin";
                                    SET gnr.chat.selected_room = roomId;
                                }
                                genro.playSound('NewMessage'); 
                                genro.dom.setClass(dojo.body(),'newMessage',true);
                            """,
                            pars="^gnr.chat.room_alert", selectedTab='=#gnr_main_left_center.selected',
                            sel_room='=gnr.chat.selected_room',rooms='=gnr.chat.rooms')
        pane.dataController("""
                              var unread = rooms.sum('unread');
                              genro.dom.setClass(dojo.body(),'newMessage',unread>0);
                              """, rooms='=gnr.chat.rooms', _fired='^gnr.chat.calc_unread')


    def ct_chat_form(self, frame):
        bar = frame.top.bar

        self.ct_controller_main(bar)
        bar.dataController("ct_chat_utils.read_msg(_node.getValue());", msgbag="^gnr.chat.msg")

        frame.center.tabContainer(nodeId='ct_chat_rooms', margin='5px', _class='chat_rooms_tab',
                        selectedPage='^.selected_room')
        bar.dataController("""

                             var roombag = rooms.getItem(sel_room);
                             roombag.setItem('unread',null);
                             FIRE gnr.chat.calc_unread;
                             ct_chat_utils.fill_title(roombag);
                            """, sel_room='^.selected_room', rooms='=.rooms',_if='rooms&&sel_room')

        bar.dataController("""
            var roombag =this.getRelativeData("gnr.chat.rooms."+roomId);
            var msg = roombag.getItem('current_msg');
            roombag.setItem('current_msg','');
            var chat = genro.chat();
            var textbox = dojo.byId("ct_msgtextbox_"+roomId);
            if(textbox){
                textbox.focus();
            }
            if(msg.indexOf('/')==0){
                msg = msg.slice(1).split(' ');
                var command = msg[0];
                msg = msg.slice(1).join(' ');
                var msg = chat.processCommand(command,msg,roomId);
                if(msg && msg.indexOf('*error:')==0){
                    alert(msg.slice(1));
                    msg=false;
                }

            }
            for(var rpcl in chat.replacers){
                msg = msg.replace(new RegExp(rpcl),
                            function(path) {
                                return chat.callReplacer(rpcl,path,roomId,msg);
                            });
            }
            if(msg!==false){
                PUBLISH ct_send_message = {roomId:roomId,msg:msg};
            }


            """,subscribe_ct_typed_message=True)
        bar.dataRpc('dummy', self.ct_send_message, subscribe_ct_send_message=True,
                    _onCalling="""
                                var roombag =this.getRelativeData("gnr.chat.rooms."+roomId);
                                if (!msg && !kwargs.disconnect){
                                    return false;
                                }
                                kwargs.users=roombag.getItem('users');""")

    def ct_chat_grid(self, button):
        tp = button.tooltipPane(onOpening=""" var users = genro.getData('gnr.chat.connected_users');
                                                setTimeout(function(){
                                                    genro.getFrameNode('ct_connected_user').widget.resize();
                                                    genro.setData('gnr.chat.grid_users.store',users.deepCopy());
                                                },1)
                                                """)
        frame = tp.framePane(frameCode='ct_connected_user',height='400px',width='230px',_class='noheader ct_chatgrid')

        frame.data('.grid_users', Bag())
        frame.dataRemote('gnr.chat.connected_users', 'connection.connected_users_bag',cacheTime=2)

        def struct(struct):
            r = struct.view().rows()
            r.cell('user_name', dtype='T', name='Fullname', width='100%')

        bar = frame.top.slotToolbar('5,vtitle,*,searchOn',height='20px',font_size='.9em')
        bottom = frame.bottom.slotBar('*,openchat,2',font_size='.9em',padding='2px',border_top='1px solid silver')
        bottom.openchat.button('!!Start chat',action='FIRE #ct_connected_user_grid.open_chat; tp.widget.onCancel();',tp=tp,
                                disabled='^#ct_connected_user_grid.selectedIndex?=(#v==null)')
        bar.vtitle.div('!!Users',color='#666')
        frame.includedview(identifier='user',
                           datapath='.grid_users',
                           selectedIndex='.selectedIndex',
                           storepath='.store',
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
    def ct_send_message(self, msg=None, roomId=None, users=None, disconnect=False, priority='L',**kwargs):
        ts = self.toText(datetime.now(), format='HH:mm:ss')
        if msg and msg.startswith('!'):
            priority='H'
            msg=msg[1:]
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
                self.setInClientData(path='gnr.chat.room_alert', value=Bag(dict(roomId=roomId, users=users, priority=priority)),
                                     filters='user:%s' % user, fired=True, reason='chat_open',
                                     public=True, replace=True)

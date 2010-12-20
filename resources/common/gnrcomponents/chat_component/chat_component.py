# -*- coding: UTF-8 -*-

# chat_component.py
# Created by Francesco Porcari on 2010-09-08.
# Copyright (c) 2010 Softwell. All rights reserved.

from gnr.web.gnrwebpage import BaseComponent
from gnr.core.gnrbag import Bag
from datetime import datetime

class ChatComponent(BaseComponent):
    py_requires='foundation/includedview:IncludedView'
    css_requires = 'gnrcomponents/chat_component/chat_component'
    js_requires='gnrcomponents/chat_component/chat_component'
    def mainLeft_chat_plugin(self,pane):
        """!!Chat"""          
        self.ct_chat_main(pane.borderContainer())
        
    def ct_chat_main(self,bc):
        toolbar = bc.contentPane(region='top').toolbar()
        ttdialog = toolbar.dropDownButton(label='User').tooltipDialog(title='!!Users list',datapath='gnr.chat',nodeId='ct_chat_list_users_dlg',
                                                                     connect_onOpen='genro.wdgById("ct_chat_list_users").resize(); FIRE .listusers;'
                                                                     ).borderContainer(height='300px',width='250px',nodeId='ct_chat_list_users')
        self.ct_chat_grid(ttdialog)
        self.ct_chat_form(bc.borderContainer(region='center',datapath='gnr.chat',margin='3px'))

    def ct_controller_main(self,pane):
        pane.dataRpc('dummy','setStoreSubscription',subscribe_chat_plugin_on=True,
                    storename='user',client_path='gnr.chat.msg',active=True,
                    _onResult='genro.rpc.setPolling(2,2);  dojo.removeClass(dojo.body(),"newMessage");')
        pane.dataRpc('dummy','setStoreSubscription',active=False,subscribe_chat_plugin_off=True,storename='user',
                    _onCalling='genro.rpc.setPolling();')
                    
        pane.dataController("genro.playSound('NewMessage'); dojo.addClass(dojo.body(),'newMessage');",
                            user="^gnr.chat.room_alert",_if='selectedTab!="chat_plugin"',selectedTab='=#gnr_main_left_center.selected')
        
    
    def ct_chat_form(self,bc):
        self.ct_controller_main(bc)
        
        bc.dataController("""SET gnr.chat.curr_address = 'gnr.chat.rooms.'+user;
                               """,user='^#ct_connected_user_grid.selectedId',
                               _if='user',_else='SET gnr.chat.disabled=true;')
        bc.dataController("""
                            var grid = genro.wdgById(gridId);
                            var rows = grid.getSelectedNodes();
                            var users =new gnr.GnrBag();
                            dojo.forEach(rows,function(n){users.setItem(n.attr.user,null,{user_name:n.attr.user_name,user:n.attr.user})});
                            var roomId= new Date().getTime();
                            ct_chat_utils.open_chat(roomId,users);
                            """,
                            _fired="^#ct_connected_user_grid.open_chat",
                            gridId='ct_connected_user_grid')
        
        bc.dataController("ct_chat_utils.read_msg(msgbag,_node);",msgbag="^gnr.chat.msg")
        
        bc.tabContainer(region='center',nodeId='ct_chat_rooms',margin='5px',_class='chat_rooms_tab',
                         selectedPage='^.selected_room')
        bc.dataRpc('dummy','ct_send_message',_if='msg',subscribe_ct_send_message=True,
                    _onResult='dojo.byId("ct_msgtextbox_"+kwargs.roomId).focus();')
    
    def ct_chat_grid(self,bc):
        bc.data('.grid_users',Bag())
        bc.dataRpc('.connected_users','connection.connected_users_bag',_fired='^.listusers',exclude='==_users.keys()',_users='=.grid_users')
        def struct(struct):
            r = struct.view().rows()
            r.cell('user_name', dtype='T', name='Fullname', width='16em')
            return struct
        def footer(pane):
            pane.button('Confirm',action='FIRE .open_chat;genro.wdgById("ct_chat_list_users_dlg").onCancel();')
        self.includedViewBox(bc,nodeId='ct_connected_user_grid',
                            identifier='user',
                            datapath='.grid_users',filterOn='!!Search:user_name',
                            storepath='gnr.chat.connected_users',
                            footer=footer,
                            label='!!Users',
                            connect_onRowDblClick="""
                                                    FIRE .open_chat;
                                                    genro.wdgById("ct_chat_list_users_dlg").onCancel();
                                                    """ ,
                            struct=struct, autoWidth=True)

    def rpc_ct_send_message_old(self,user=None,msg=None):
        ts=self.toText(datetime.now(),format='HH:mm:ss')
        path = 'gnr.chat.msg' 
        with self.userStore(self.user) as store:
            store.set_datachange(path,msg,fired=True,reason='chat_in',
                                attributes=dict(from_user=self.user,room=user,in_out='out',ts=ts))
                                
        with self.userStore(user) as store:
            store.set_datachange(path,msg,fired=True,reason='chat_out',
                                attributes=dict(from_user=self.user,room=self.user,in_out='in',ts=ts))
        self.setInClientData(path='gnr.chat.room_alert',value=self.user,
                            filters='user:%s' %user,fired=True,reason='chat_open',
                            public=True, replace=True)
                            
    def rpc_ct_send_message(self,msg=None,roomId=None,users=None):
        ts=self.toText(datetime.now(),format='HH:mm:ss')
        path = 'gnr.chat.msg' 
        for userNode in users:
            user = userNode.label
            with self.userStore(user) as store:
                in_out = 'in' if user!=self.user else 'out'
                store.set_datachange(path,Bag(dict(msg=msg,roomId=roomId,users=users)),fired=True,reason='chat_out',
                                    attributes=dict(from_user=self.user,roomId=roomId,in_out=in_out,ts=ts))
            if user!=self.user:
                self.setInClientData(path='gnr.chat.room_alert',value=Bag(dict(roomId=roomId,users=users)),
                                filters='user:%s' %user,fired=True,reason='chat_open',
                                public=True, replace=True)
    
    def rpc_ct_remove_chat(self):
        pass
        
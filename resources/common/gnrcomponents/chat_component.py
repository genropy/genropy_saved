# -*- coding: UTF-8 -*-

# chat_component.py
# Created by Francesco Porcari on 2010-09-08.
# Copyright (c) 2010 Softwell. All rights reserved.

from gnr.web.gnrwebpage import BaseComponent
from gnr.core.gnrbag import Bag
from datetime import datetime

class ChatComponent(BaseComponent):
    py_requires='foundation/includedview:IncludedView'
    def pbl_left_chat(self,pane,footer=None,toolbar=None):
        "Chat"
        footer.button('!!Chat',showLabel=False,
             action="""SET gnr.chat.buttonIcon = 'icnBuddy';
                        SET pbl.left_stack = "chat";
                        """,
             iconClass='^gnr.chat.buttonIcon',default_iconClass='icnBuddy',float='right',nodeId='ct_button_footer')
        footer.dataRpc('dummy','setStoreSubscription',subscribe='==_selected_stack=="chat"',
                    _selected_stack='^pbl.left_stack',storename='user',client_path='gnr.chat.msg')
                    
        ttdialog = toolbar.dropDownButton(label='User').tooltipDialog(title='!!Users list',datapath='gnr.chat',nodeId='ct_chat_list_users_dlg',
                                                                     connect_onOpen='genro.wdgById("ct_chat_list_users").resize(); FIRE .listusers;'
                                                                     ).borderContainer(height='300px',width='250px',nodeId='ct_chat_list_users')        
        self.ct_chat_grid(ttdialog)
        self.ct_chat_form(pane.borderContainer(datapath='gnr.chat'))

        
    def ct_chat_form(self,bc):
        bc.dataController("""SET gnr.chat.curr_address = 'gnr.chat.rooms.'+user;
                               """,user='^#ct_connected_user_grid.selectedId',
                               _if='user',_else='SET gnr.chat.disabled=true;')
        bc.dataRpc('dummy','setStoreSubscription',subscribe=True,
                    storename='user',client_path='gnr.chat.rooms',_onStart=True)
        bc.dataController("""
                            SET gnr.chat.buttonIcon = 'icnBuddyChat'
                            """,user="^gnr.chat.rooms")
        bc.script("""
                    var ct_chat_utils = {};
                    ct_chat_utils.open_chat = function(user){
                        var roomsNode = genro.nodeById('ct_chat_rooms');
                        var roomTab =  genro.nodeById(user+'_room');
                        if (!roomTab){
                            roomTab = roomsNode._('ContentPane',{pageName:user,overflow:'auto',title:user,
                                                            margin:'4px',background:'white',border:'1px solid gray',
                                                            id:user+'_room'});
                            roomsNode.widget.resize();
                        }
                        dojo.byId("ct_msgtextbox").focus();

                    };
                    """)
        bc.dataController("""
                            ct_chat_utils.open_chat(selected_user);
                            SET .selected_room = selected_user;
                            """,selected_user="^#ct_connected_user_grid.open_chat")
        
        bc.dataController("""
            var msgnode,attrs,room,roomNode,message;
            msgnode = _node;
            attrs = msgnode.attr;
            room = attrs.room;
            roomNode = dojo.byId(room+'_room');
            console.log(attrs["ts"]);
            if(!roomNode){
                ct_chat_utils.open_chat(room);
                roomNode = dojo.byId(room+'_room');
            }
            message = roomNode.lastElementChild;
            if(!message||(message.from_user!=attrs['from_user'])){
                message = document.createElement('div');
                message.innerHTML = '<div class="ct_msglbl"> <div class="ct_msglbl_from">'+attrs["from_user"]+'</div><div class="ct_msglbl_ts">'+genro.format(attrs["ts"],{time:'medium'})+'</div></div><div class="ct_msgbody"></div>';
                dojo.addClass(message,attrs['in_out']=='in'?'ct_inmsg':'ct_outmsg');
                dojo.addClass(message,'ct_msgblock');
                message.from_user =  attrs['from_user'];
                roomNode.appendChild(message);
            }
            var msgrow =  document.createElement('div');
            dojo.addClass(msgrow,'ct_msgrow');
            msgrow.innerHTML = msgtxt;
            message.lastElementChild.appendChild(msgrow);
            roomNode.scrollTop = roomNode.scrollHeight;
        """,msgtxt="^gnr.chat.msg")
        
        bottom = bc.contentPane(region='bottom',onEnter='FIRE .send;',height='30px',overflow='hidden')
       # bottom.dataController("console.log(room);",room="^.selected_room",_onStart=True)
        bottom = bottom.div(position='absolute',top='4px',bottom='4px',left='4px',right='4px',padding_left='1px',
                        padding_right='8px',padding_bottom='1px',padding_top='1px',visible='^.selected_room',
                            default_visible=False)
        bottom.textbox(value='^.message',ghost='Write message',width='100%',padding='2px',id='ct_msgtextbox')      
        bc.tabContainer(region='center',nodeId='ct_chat_rooms',margin='5px',
                         selectedPage='^.selected_room')        
        bc.dataRpc('dummy','ct_send_message',user='=.selected_room',
                    msg='=.message',_fired='^.send',_if='user&&msg',_onResult='SET .message="";dojo.byId("ct_msgtextbox").focus();')
        
    def ct_chat_grid(self,bc):
        bc.dataRpc('.connected_users','ct_get_connected_users',_fired='^.listusers')
        def struct(struct):
            r = struct.view().rows()
            r.cell('user_name', dtype='T', name='Fullname', width='16em')
            return struct
        self.includedViewBox(bc,nodeId='ct_connected_user_grid',
                            datapath='.grid_users',filterOn='!!Search:user_name',
                            storepath='gnr.chat.connected_users',
                            label='!!Users',
                            connect_onRowDblClick="""
                                                    genro.wdgById("ct_chat_list_users_dlg").onCancel();
                                                    FIRE .open_chat = this.widget.rowIdByIndex($1.rowIndex);;
                                                    """ ,
                            struct=struct, autoWidth=True)
    
    def rpc_ct_get_connected_users(self):
        users = self.site.register.users()   
        result = Bag()
        for user,arguments in users.items():
            arguments.pop('connections',None)
            if user != self.user:
                arguments['_pkey'] = user
                arguments.pop('datachanges',None)
                arguments['user_name'] = arguments['user_name'] or user
                result.setItem(user,None,**arguments)
        return result
    
    def rpc_ct_send_message(self,user=None,msg=None):
        ts=self.toText(datetime.now(),format='HH:mm:ss')
        path = 'gnr.chat.msg' 
        with self.userStore(self.user) as store:
            store.set_datachange(path,msg,fired=True,reason='chat_in',
                                attributes=dict(from_user=self.user,room=user,in_out='out',ts=ts))
                                
        with self.userStore(user) as store:
            store.set_datachange(path,msg,fired=True,reason='chat_out',
                                attributes=dict(from_user=self.user,room=self.user,in_out='in',ts=ts))
            store.set_datachange('gnr.chat.rooms',self.user,fired=True,reason='chat_open')
        
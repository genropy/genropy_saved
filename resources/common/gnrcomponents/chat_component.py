# -*- coding: UTF-8 -*-

# chat_component.py
# Created by Francesco Porcari on 2010-09-08.
# Copyright (c) 2010 Softwell. All rights reserved.

from gnr.web.gnrwebpage import BaseComponent
from gnr.core.gnrbag import Bag
from datetime import datetime

class ChatComponent(BaseComponent):
    py_requires='foundation/includedview:IncludedView'
    def pbl_left_chat(self,pane,toolbar=None):
        "Chat"
        toolbar.button('!!Chat',showLabel=False,
             action='SET pbl.left_stack = "chat";',
             iconClass='icnBaseEditUser',float='right')
        bc = pane.borderContainer(datapath='gnr.chat')
        self.ct_chat_grid(bc.borderContainer(region='top',height='30%',splitter=True))
        self.ct_chat_form(bc.borderContainer(region='center'))

        
    def ct_chat_form(self,bc):
        bc.dataController("""SET gnr.chat.curr_address = 'gnr.chat.rooms.'+user;
                               SET gnr.chat.disabled=false;
                               """,user='^#ct_connected_user_grid.selectedId',
                               _if='user',_else='SET gnr.chat.disabled=true;')
        bc.dataRpc('dummy','setStoreSubscription',subscribe='==_selected_stack=="chat"',
                    _selected_stack='^pbl.left_stack',storename='user',client_path='gnr.chat')
        
        bc.dataController("""var msgnode = _node;
                               var attrs = msgnode.attr;
                               var room = attrs.room;
                               var roomNode = genro.nodeById(room+'_room');
                               var message = roomNode._('div',{_class:attrs['in_out']=='in'?'ct_inmsg':'ct_outmsg'});
                               message._('div',{content:attrs['from_user'],_class:'ct_msglbl'})
                               message._('div',{content:msgtxt});
                           """,msgtxt="^gnr.chat.msg")
                           
        bc.dataController("""var roomsNode = genro.nodeById('ct_chat_rooms');
                             console.log(selected_user);
                             console.log(selected_user in roomsNode.widget.gnrPageDict);
                             if (!(selected_user in roomsNode.widget.gnrPageDict)){
                                roomsNode._('ContentPane',{pageName:selected_user,overflow:'auto'})._('div',{margin:'4px',nodeId:selected_user+'_room'});
                             }
                             SET .selected_room = selected_user;
                             """,
                            selected_user="^#ct_connected_user_grid.selectedId")
        bc.contentPane(region='bottom',onEnter='FIRE .send;',height='30px',overflow='hidden',
                        ).textbox(value='^.message',ghost='Write message',padding='3px',
                                    disabled='^gnr.chat.disabled',width='95%',margin_left='5px')      
        bc.stackContainer(region='center',nodeId='ct_chat_rooms',background='white',margin='5px',
                         selectedPage='^.selected_room')        
        bc.dataRpc('dummy','ct_send_message',user='=#ct_connected_user_grid.selectedId',
                    msg='=.message',_fired='^.send',_if='user&&msg',_onResult='SET .message="";')

       #fb.dataController("""
       #                    var rootnode= genro.nodeById("ct_chat_monitor");
       #                    var domNode = rootnode.domNode;
       #                    rootnode.clearValue().freeze();
       #                    rows.forEach(function(n){
       #                        var attr = n.attr;
       #                        var msgattr = {};
       #                        msgattr['background_color'] = attr['in_out']=='out'?'lightgreen':'lightblue';
       #                        msgattr['_class'] = 'shadow_2 rounded_min';
       #                        msgattr['margin_right'] = attr['in_out']=='out'?'25px':'3px';
       #                        msgattr['margin_left'] = attr['in_out']=='out'?'3px':'25px';
       #                        msgattr['margin_top'] = '5px';
       #                        msgattr['padding'] = '3px';
       #                        msgattr['font_size'] ='.9em';
       #                        msgattr['text_align'] = attr['in_out']=='out'?'left':'right';
       #                        msgattr.content = n.getValue();
       #                        rootnode._('div',msgattr);
       #                    });
       #                    rootnode.unfreeze();
       #                    var scrollHeight = rootnode.domNode.scrollHeight;
       #                    var clientHeight = rootnode.domNode.clientHeight;
       #                    var scrollTop;
       #                    if (scrollHeight>clientHeight){
       #                        scrollTop = scrollHeight-domNode.scrollWidth;
       #                    }
       #                    if (scrollTop){
       #                        rootnode.domNode.scrollTop = scrollTop;
       #                    }
       #                    
       #                    """,rows="^.rows",datapath='^gnr.chat.curr_address',_if='rows',font_size='.8em')



        
        
    def ct_chat_grid(self,bc):
        bc.dataRpc('.connected_users','ct_get_connected_users',_timing=30,
                        _if='_page=="chat"',_page='^pbl.left_stack')
        def struct(struct):
            r = struct.view().rows()
            r.cell('user_name', width='20em',name='Fullname')
            return struct
        self.includedViewBox(bc,nodeId='ct_connected_user_grid',
                            datapath='.grid_users',
                            storepath='gnr.chat.connected_users',
                            label='Current users',
                            autoSelect=True,
                            struct=struct, autoWidth=True)
    
    def rpc_ct_get_connected_users(self):
        users = self.site.register.users()   
        result = Bag()
        for user,arguments in users.items():
            arguments.pop('connections',None)
            if user != self.user:
                arguments['_pkey'] = user
                arguments.pop('datachanges',None)
                result.setItem(user,None,**arguments)
        return result
    
    def rpc_ct_send_message(self,user=None,msg=None):
        ts = datetime.now()
        path = 'gnr.chat.msg' 
        with self.userStore(self.user) as store:
            store.set_datachange(path,msg,fired=True,reason='chat_in',
                                attributes=dict(from_user=self.user,room=user,in_out='out',ts=ts))
        with self.userStore(user) as store:
            store.set_datachange(path,msg,fired=True,reason='chat_out',
                                attributes=dict(from_user=self.user,room=self.user,in_out='in',ts=ts))
        
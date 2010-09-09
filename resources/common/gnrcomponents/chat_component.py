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
        self.ct_chat_form(bc.contentPane(region='bottom'))
        self.ct_chat_grid(bc.borderContainer(region='center'))
        
    def ct_chat_form(self,pane):
        pane.dataController("""SET gnr.chat.curr_address = 'gnr.chat.rooms.'+user;
                               SET gnr.chat.disabled=false;
                               """,user='^#ct_connected_user_grid.selectedId',
                               _if='user',_else='SET gnr.chat.disabled=true;')
                         
        fb = pane.formbuilder(cols=1, border_spacing='4px',
                            disabled='^gnr.chat.disabled',onEnter='FIRE .send;',
                            width='90%',margin='5px')
        fb.dataController("""
                            var rootnode= genro.nodeById("ct_chat_monitor");
                            var domNode = rootnode.domNode;
                            rootnode.clearValue().freeze();
                            rows.forEach(function(n){
                                var attr = n.attr;
                                var msgattr = {};
                                msgattr['background_color'] = attr['in_out']=='out'?'lightgreen':'lightblue';
                                msgattr['_class'] = 'shadow_2 rounded_min';
                                msgattr['margin_right'] = attr['in_out']=='out'?'25px':'3px';
                                msgattr['margin_left'] = attr['in_out']=='out'?'3px':'25px';
                                msgattr['margin_top'] = '5px';
                                msgattr['padding'] = '3px';
                                msgattr['font_size'] ='.9em';
                                msgattr['text_align'] = attr['in_out']=='out'?'left':'right';
                                msgattr.content = n.getValue();
                                rootnode._('div',msgattr);
                            });
                            rootnode.unfreeze();
                            var scrollHeight = rootnode.domNode.scrollHeight;
                            var clientHeight = rootnode.domNode.clientHeight;
                            var scrollTop;
                            if (scrollHeight>clientHeight){
                                scrollTop = scrollHeight-domNode.scrollWidth;
                            }
                            if (scrollTop){
                                rootnode.domNode.scrollTop = scrollTop;
                            }
                            
                            """,rows="^.rows",datapath='^gnr.chat.curr_address',_if='rows',font_size='.8em')
        fb.div(innerHTML='=="Chat with "+_user',font_size='.8em',
                _user='^#ct_connected_user_grid.selectedId?user_name',font_weight='bold')
        fb.div(nodeId='ct_chat_monitor',height='200px',width='100%',
                 background='white',border='1px solid gray',
                 _class='shadow_2',padding='5px',overflow='auto')
        fb.textbox(value='^.message',width='100%',ghost='Write message',padding='3px')
        fb.dataRpc('dummy','ct_send_message',user='=#ct_connected_user_grid.selectedId',
                    msg='=.message',_fired='^.send',_if='user&&msg',_onResult='SET .message="";')

        
        
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
                arguments.pop('datachanges')
                result.setItem(user,None,**arguments)
        return result
    
    def rpc_ct_send_message(self,user=None,msg=None):
        ts = datetime.now()
        path = 'gnr.chat.rooms.%s.rows.#id' 
        with self.userStore(self.user) as store:
            store.set_datachange(path %user,msg,fired=False,reason='chat_in',
                                attributes=dict(from_user=self.user,in_out='out',ts=ts))
        with self.userStore(user) as store:
            store.set_datachange(path %self.user,msg,fired=False,reason='chat_out',
                                attributes=dict(from_user=self.user,in_out='in',ts=ts))
        
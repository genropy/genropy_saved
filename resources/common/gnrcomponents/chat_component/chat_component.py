# -*- coding: UTF-8 -*-

# chat_component.py
# Created by Francesco Porcari on 2010-09-08.
# Copyright (c) 2010 Softwell. All rights reserved.

from gnr.web.gnrwebpage import BaseComponent
from gnr.core.gnrbag import Bag
from datetime import datetime

class ChatComponent(BaseComponent):
    py_requires='foundation/includedview:IncludedView'
    js_requires='gnrcomponents/chat_component/chat_component'
    def mainLeft_chat_plugin(self,tc):
        """!!Chat"""          
        tc.data('gnr.chat.buttonIcon','icnBuddy')
        tc.dataController("""var kw = _triggerpars.kw;
                             var nodelist = dojo.query('.'+kw.oldvalue); 
                             nodelist.removeClass(kw.oldvalue);
                             nodelist.addClass(newicon);
                             """,
                             newicon="^gnr.chat.buttonIcon")
        
        self.ct_chat_main(tc.borderContainer(title='!!Chat',pageName='chat_plugin',
                                            iconClass='=gnr.chat.buttonIcon'))
        
    def ct_chat_main(self,bc):
        toolbar = bc.contentPane(region='top').toolbar()
        ttdialog = toolbar.dropDownButton(label='User').tooltipDialog(title='!!Users list',datapath='gnr.chat',nodeId='ct_chat_list_users_dlg',
                                                                     connect_onOpen='genro.wdgById("ct_chat_list_users").resize(); FIRE .listusers;'
                                                                     ).borderContainer(height='300px',width='250px',nodeId='ct_chat_list_users')
        self.ct_chat_grid(ttdialog)
        self.ct_chat_form(bc.borderContainer(region='center',datapath='gnr.chat'))

    def ct_controller_main(self,pane):
        
        pane.dataRpc('dummy','setStoreSubscription',subscribe_chat_plugin_open=True,
                    storename='user',client_path='gnr.chat.msg',active=True,
                    _onResult='genro.rpc.setPolling(2,2); SET gnr.chat.buttonIcon = "icnBuddy";')
        pane.dataRpc('dummy','setStoreSubscription',active=False,subscribe_chat_plugin_close=True,storename='user',
                    _onCalling='genro.rpc.setPolling();')
                    
        pane.dataController("genro.playSound('NewMessage'); SET gnr.chat.buttonIcon = 'icnBuddyChat';",
                            user="^gnr.chat.room_alert",_if='selectedTab!="chat"',selectedTab='=.selected')
        
    
    def ct_chat_form(self,bc):
        self.ct_controller_main(bc)
        
        bc.dataController("""SET gnr.chat.curr_address = 'gnr.chat.rooms.'+user;
                               """,user='^#ct_connected_user_grid.selectedId',
                               _if='user',_else='SET gnr.chat.disabled=true;')
        bc.dataController("""
                            ct_chat_utils.open_chat(selected_user);
                            SET .selected_room = selected_user;
                            """,selected_user="^#ct_connected_user_grid.open_chat")
        
        bc.dataController("""
            ct_chat_utils.read_msg(_node,msgtxt);
        """,msgtxt="^gnr.chat.msg")
        
        bottom = bc.contentPane(region='bottom',onEnter='FIRE .send;',height='30px',overflow='hidden')
        bottom = bottom.div(position='absolute',top='4px',bottom='4px',left='4px',right='4px',padding_left='1px',
                        padding_right='8px',padding_bottom='1px',padding_top='1px',visible='^.selected_room',
                            default_visible=False)
        
        bottom.textbox(value='^.message',ghost='Write message',width='100%',padding='2px',id='ct_msgtextbox')      
        bc.tabContainer(region='center',nodeId='ct_chat_rooms',margin='5px',
                         selectedPage='^.selected_room')        
        bc.dataRpc('dummy','ct_send_message',user='=.selected_room',
                    msg='=.message',_fired='^.send',_if='user&&msg',
                    _onResult='SET .message="";dojo.byId("ct_msgtextbox").focus();')
        
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
            if user != self.user and not user.startswith('guest_'):
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
        self.setInClientData(path='gnr.chat.room_alert',value=self.user,
                            filters='user:%s' %user,fired=True,reason='chat_open',
                            public=True, replace=True)
        
# -*- coding: UTF-8 -*-

from gnr.web.gnrwebpage import BaseComponent

class ChatComponent(BaseComponent):
    py_requires='gnrcomponents/chat_component'
    def pbl_left_chat(self,pane,footer=None,toolbar=None):
        "Chat"
        footer.button('!!Chat',showLabel=False,
             action="""SET gnr.chat.buttonIcon = 'icnBuddy';
                       PUBLISH ct_chat_open;
                        """,
             iconClass='^gnr.chat.buttonIcon',default_iconClass='icnBuddy',float='right',nodeId='ct_button_footer')
        ttdialog = toolbar.dropDownButton(label='User').tooltipDialog(title='!!Users list',datapath='gnr.chat',nodeId='ct_chat_list_users_dlg',
                                                                     connect_onOpen='genro.wdgById("ct_chat_list_users").resize(); FIRE .listusers;'
                                                                     ).borderContainer(height='300px',width='250px',nodeId='ct_chat_list_users')        
        pane.dataController("SET pbl.left_stack = 'chat';",subscribe_ct_chat_open=True)
        pane.dataController("""
                            if(pbl_left_stack_selected[0]=='chat_hide'){
                                PUBLISH ct_chat_close;
                            };
                            """,subscribe_pbl_left_stack_selected=True,subscribe_pbl_mainMenuStatus=True,
                            _if='_reason=="pbl_left_stack_selected";',
                            _else='if(pbl_mainMenuStatus==false){PUBLISH ct_chat_close;}')
        
        pane.dataController("SET gnr.chat.buttonIcon = 'icnBuddyChat';",subscribe_ct_room_alert=True,
                            _if='selectedStack!="chat"',selectedStack='=pbl.left_stack')
        self.ct_chat_grid(ttdialog)
        self.ct_chat_form(pane.borderContainer(datapath='gnr.chat'))
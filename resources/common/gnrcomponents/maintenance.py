# -*- coding: UTF-8 -*-

# chat_component.py
# Created by Francesco Porcari on 2010-09-08.
# Copyright (c) 2011 Softwell. All rights reserved.

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method
from gnr.core.gnrbag import Bag

class MaintenancePlugin(BaseComponent):
    def mainLeft_maintenance(self, pane):
        """!!Maintenance"""
        frame = pane.framePane(datapath='gnr.maintenance')
        tc = frame.center.tabContainer(margin='2px')
        self.maintenance_backup(tc.framePane(title='Backup',margin='2px',rounded=4,border='1px solid silver'))
        self.maintenance_register(tc.framePane(title='!!Users & Connections',margin='2px',rounded=4,border='1px solid silver'))

    def maintenance_backup(self,frame):
        bar = frame.top.slotToolbar('5,backup,*')
        #top = bc.contentPane(region='top',_class='pbl_roundedGroup',margin='2px')
        #top.div('!!Backups',_class='pbl_roundedGroupLabel')
        #fb = top.formbuilder(cols=1,border_spacing='3px')
        bar.backup.button('Complete Backup',action='PUBLISH table_script_run = {res_type:"action",resource:"dumpall",table:"adm.backup"};')

    def maintenance_register(self,frame):
        frame.css('.disconnected .dojoxGrid-cell', "color:red !important;")
        frame.css('.inactive .dojoxGrid-cell', "color:orange !important;")
        frame.css('.no_children .dojoxGrid-cell', "color:yellow !important;")
        bar = frame.top.slotToolbar('5,stackButtons,*,cleanIdle,5')
        bar.cleanIdle.button('Clean')


        sc = frame.center.stackContainer()

        bc = sc.borderContainer(title='Users')
        messageframe = bc.framePane(region='bottom',height='150px',_class='pbl_roundedGroup',margin='2px')
        messageframe.top.slotBar('2,vtitle,*',vtitle='!!Message',_class='pbl_roundedGroupLabel')
        footer = messageframe.bottom.slotBar('2,flush,*,userMessage,2',_class='slotbar_dialog_footer')
        messageframe.center.simpleTextArea(value='^maintenance.userframe.message')
        footer.userMessage.button('Service message',action='FIRE gnr.maintenance.logout_message')
        footer.dataRpc('dummy',self.sendMessageToClient,_fired='^gnr.maintenance.logout_message',
                        message='==_message || _def_message',
                        _def_message='!!The system is going to be restarted. Finish your pending tasks',
                        _message='=maintenance.userframe.message',
                        pageId='*',filters='*')
        footer.flush.button('Flush memcached',action='FIRE .resetMemcached')
        footer.dataRpc('dummy',self._maintenance_resetMemcached,_fired='^.resetMemcached',_ask='!!You are going to stop every user activity')


        userframe = bc.contentPane(region='center').frameGrid(frameCode='connectedUsers',struct=self.connected_users_struct,
                                                                        grid_userSets='.sets',
                                                                            datapath='.connectedUsers',margin='2px',_class='pbl_roundedGroup')
        userframe.grid.bagStore(storepath='gnr.maintenance.data.user',storeType='AttributesBagRows',
                                data='^gnr.maintenance.data.loaded_users',selfUpdate=True)
        bar = userframe.top.slotBar('2,exclude_guest,*,searchOn,2',vtitle='Connected user',_class='pbl_roundedGroupLabel')
        bar.exclude_guest.checkbox(value='^.exclude_guest',label='!!Exclude guest')
        frame.dataRpc('dummy',self.maintenance_update_data,_tab='^left.selected',exclude_guest='=.connectedUsers.exclude_guest',
            _if='_tab=="maintenance"',
            _onResult="""SET gnr.maintenance.data.loaded_users = result.popNode("users");
                         SET gnr.maintenance.data.loaded_connections = result.popNode("connections");
                         SET gnr.maintenance.data.loaded_pages = result.popNode("pages");""",_timing=5,
            sysrpc=True)

        pagesframe = sc.contentPane(title='Pages').frameGrid(frameCode='currentPages',struct=self._page_grid_struct,
                        datapath='.currentPages',
                        title='Pages',pbl_classes=True,margin='2px',_class='pbl_roundedGroup')
        pagesframe.grid.bagStore(storepath='gnr.maintenance.data.pages',storeType='AttributesBagRows',
                                data='^gnr.maintenance.data.loaded_pages',selfUpdate=True)
        bar = pagesframe.top.slotBar('2,vtitle,*,searchOn,2',vtitle='Connected user',_class='pbl_roundedGroupLabel')

        connectionframe = sc.contentPane(title='Connections').frameGrid(frameCode='currentConnections',struct=self._connection_grid_struct,
                        datapath='.currentConnections',
                        title='Connections',pbl_classes=True,margin='2px',_class='pbl_roundedGroup')
        connectionframe.grid.bagStore(storepath='gnr.maintenance.data.pages',storeType='AttributesBagRows',
                                data='^gnr.maintenance.data.loaded_connections',selfUpdate=True)
        bar = connectionframe.top.slotBar('2,vtitle,*,searchOn,2',vtitle='Connections',_class='pbl_roundedGroupLabel')

    @public_method
    def _maintenance_resetMemcached(self):
        self.site.shared_data.flush_all()

    def _page_grid_struct(self, struct):
        r = struct.view().rows()
        r.cell('register_item_id', width='14em', name='Page id')
        r.cell('user', width='6em', name='User')
        r.cell('user_ip', width='6em', name='User ip')
        #r.cell('start_ts', width='11em', name='Start', dtype='DH')
        r.cell('pagename', width='8em', name='Pagename')
        r.cell('age', width='6em', dtype='L', name='Conn.Time',format='DHMS')
        #r.cell('last_rpc_age', width='6em', dtype='L', name='Last RPC',format='DHMS')
        r.cell('last_event_age', width='6em', dtype='L', name='Last Act.',format='DHMS')
        r.cell('alive',width='4em',semaphore=True,name='Alive',dtype='B')


    def _connection_grid_struct(self, struct):
        r = struct.view().rows()
        #r.cell('register_item_id', width='14em', name='Connection id')
        r.cell('user', width='6em', name='User')
        r.cell('user_ip', width='8em', name='IP')
        r.cell('browser_name', width='10em', name='Browser')
        r.cell('age', width='6em', dtype='L', name='Conn.Time',format='DHMS')
        #r.cell('last_rpc_age', width='4em', dtype='L', name='L.RPC')
        r.cell('last_event_age', width='6em', dtype='L', name='Last Act.',format='DHMS')
        r.cell('alive',width='4em',semaphore=True,name='Alive',dtype='B')

    def connected_users_struct(self,struct):
        r = struct.view().rows()
        r.cell('_checked',userSets=True,name=' ')
        r.cell('user', width='6em', name='User')
        r.cell('age', width='8em', dtype='L', name='Conn.Time',format='DHMS')
       # r.cell('last_rpc_age', width='6em', dtype='L', name='Last RPC',format='DHMS')
        r.cell('last_event_age', width='6em', dtype='L', name='Last Act.',format='DHMS')
        r.cell('alive',width='4em',semaphore=True,name='Alive',dtype='B')

    def btn_maintenance(self,pane,**kwargs):
        if 'superadmin' in self.userTags or '_DEV_' in self.userTags:
            pane.div(_class='button_block iframetab').div(_class='gear',tip='!!Maintenance',
                        connect_onclick="""SET left.selected='maintenance';genro.getFrameNode('standard_index').publish('showLeft');""",
                        nodeId='plugin_block_maintenance')
            
    def _maintenance_get_items(self, items, child_name=None,exclude_guest=None, **kwargs):
        result = Bag()
        for key, item in items.items():
            if exclude_guest and ( key.startswith('guest_') or item.get('user','').startswith('guest_')):
                continue
            _customClasses = []
            item['_pkey'] = key
            item['alive'] = True
            if item['last_rpc_age'] > 60:
                item['alive'] = False
                _customClasses.append('disconnected')
            elif item['last_event_age'] > 60:
                _customClasses.append('inactive')
            if child_name and not item[child_name]:
                _customClasses.append('no_children')
            item.pop('datachanges', None)
            result.setItem(key, None, _customClasses=' '.join(_customClasses),username=key, **item)
        return result

    @public_method
    def maintenance_update_data(self, exclude_guest=None,**kwargs):
        result = Bag()
        result['users'] = self._maintenance_get_items(self.site.register.users(), 'connections',exclude_guest=exclude_guest)
        connections = self.site.register.connections()
        result['connections'] = self._maintenance_get_items(connections, 'pages')
        pages = self.site.register.pages()
        result['pages'] = self._maintenance_get_items(pages,exclude_guest=exclude_guest)
        return result
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
        bc = frame.center.borderContainer()
        top = bc.contentPane(region='top',_class='pbl_roundedGroup',margin='2px')
        top.div('!!Backups',_class='pbl_roundedGroupLabel')
        fb = top.formbuilder(cols=1,border_spacing='3px')
        fb.button('Complete Backup',action='PUBLISH table_script_run = {res_type:"action",resource:"dumpall",table:"adm.backup"};')
        
        fb.button('Service logout message',action='FIRE gnr.maintenance.logout_message')
        pane.dataRpc('dummy',self.sendMessageToClient,_fired='^gnr.maintenance.logout_message',
                        message='!!The system is going to be restarted. Finish your pending tasks',pageId='*',filters='*')
            

        center = bc.tabContainer(region='center')
        userframe = center.frameGrid(frameCode='connectedUsers',struct=self.connected_users_struct,
                        storepath='gnr.maintenance.data.user',addrow=False,delrow=False,datapath='.connectedUsers',
                        title='Users',pbl_classes=True,margin='2px',_class='pbl_roundedGroup')
        bar = userframe.top.slotBar('2,exclude_guest,*,searchOn,2',vtitle='Connected user',_class='pbl_roundedGroupLabel')
        bar.exclude_guest.checkbox(value='^.exclude_guest',label='!!Exclude guest')
        center.data('.connectedUsers.exclude_guest',True)
        center.dataRpc('dummy',self.maintenance_update_data,_tab='^left.selected',exclude_guest='=.connectedUsers.exclude_guest',
            _if='_tab=="maintenance"',_onResult='SET gnr.maintenance.data.user = result.popNode("users");SET gnr.maintenance.data.pages = result.popNode("pages")',_timing=2)
        pagesframe = center.contentPane(title='Pages').frameGrid(frameCode='currentPages',struct=self._page_grid_struct,
                        storepath='gnr.maintenance.data.pages',addrow=False,delrow=False,datapath='.currentPages',
                        title='Pages',pbl_classes=True,margin='2px',_class='pbl_roundedGroup')

        bar = pagesframe.top.slotBar('2,vtitle,*,searchOn,2',vtitle='Connected user',_class='pbl_roundedGroupLabel')

    def _page_grid_struct(self, struct):
        r = struct.view().rows()
        #r.cell('register_item_id', width='14em', name='Page id')
        r.cell('user', width='6em', name='User')
        r.cell('user_ip', width='6em', name='User ip')
        r.cell('start_ts', width='11em', name='Start', dtype='DH')
        r.cell('pagename', width='8em', name='Pagename')
        r.cell('age', width='4em', dtype='L', name='Age')
        r.cell('last_rpc_age', width='4em', dtype='L', name='L.RPC')
        r.cell('last_event_age', width='4em', dtype='L', name='L.EVT')

    def connected_users_struct(self,struct):
        r = struct.view().rows()
        r.cell('user', width='6em', name='User')
        r.cell('start_ts', width='11em', dtype='DH', name='Started')
        r.cell('age', width='4em', dtype='L', name='Age')
        r.cell('last_rpc_age', width='4em', dtype='L', name='L.RPC')
        r.cell('last_event_age', width='4em', dtype='L', name='L.EVT')

    def btn_maintenance(self,pane,**kwargs):
        if 'admin' in self.userTags:
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
            if item['last_rpc_age'] > 60:
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
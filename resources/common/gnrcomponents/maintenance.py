# -*- coding: UTF-8 -*-

# chat_component.py
# Created by Francesco Porcari on 2010-09-08.
# Copyright (c) 2011 Softwell. All rights reserved.

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method
from gnr.core.gnrbag import Bag
from gnr.core.gnrstring import fromJson
from datetime import datetime


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
        messageframe.center.simpleTextArea(value='^gnr.maintenance.userframe.message')
        footer.userMessage.button('Service message',action='FIRE gnr.maintenance.logout_message')
        footer.dataRpc('dummy',self.sendMessageToClient,_fired='^gnr.maintenance.logout_message',
                        message='==_message || _def_message',
                        _def_message='!!The system is going to be restarted. Finish your pending tasks',
                        _message='=gnr.maintenance.userframe.message',
                        pageId='*',filters='*')
        footer.flush.button('Flush memcached',action='FIRE .resetMemcached')
        footer.dataRpc('dummy',self._maintenance_resetMemcached,_fired='^.resetMemcached',_ask='!!You are going to stop every user activity')


        userframe = bc.contentPane(region='center').frameGrid(frameCode='connectedUsers',struct=self.connected_users_struct,
                                                                        grid_userSets='.sets',
                                                                            datapath='.connectedUsers',margin='2px',_class='pbl_roundedGroup')
        userframe.grid.data('.sorted','username:a')
        userframe.grid.bagStore(storepath='gnr.maintenance.data.user',storeType='AttributesBagRows',
                                sortedBy='=.grid.sorted',
                                data='^gnr.maintenance.data.loaded_users',selfUpdate=True)
        bar = userframe.top.slotBar('2,exclude_guest,*,searchOn,2',vtitle='Connected user',_class='pbl_roundedGroupLabel')
        bar.exclude_guest.checkbox(value='^.exclude_guest',label='!!Exclude guest')
        frame.dataRpc('dummy',self.maintenance_update_data,_tab='^left.selected',exclude_guest='=.connectedUsers.exclude_guest',
            _if='_tab=="maintenance"',
            _onResult="""SET gnr.maintenance.data.loaded_users = result.popNode("users");
                         SET gnr.maintenance.data.loaded_connections = result.popNode("connections");
                         SET gnr.maintenance.data.loaded_pages = result.popNode("pages");""",_timing=5,
            sysrpc=True)

        pagebc = sc.borderContainer(title='Pages')
        profilepane = pagebc.contentPane(region='bottom',height='200px')
        pagesframe = pagebc.contentPane(region='center').frameGrid(frameCode='currentPages',struct=self._page_grid_struct,
                        datapath='.currentPages',
                        title='Pages',pbl_classes=True,margin='2px',_class='pbl_roundedGroup')
        pagesframe.grid.data('.sorted','age:d')
        pagesframe.grid.bagStore(storepath='gnr.maintenance.data.pages',storeType='AttributesBagRows',
                                sortedBy='=.grid.sorted',
                                data='^gnr.maintenance.data.loaded_pages',selfUpdate=True)
        bar = pagesframe.top.slotBar('2,vtitle,*,searchOn,2',vtitle='Connected user',_class='pbl_roundedGroupLabel')
        pagesframe.dataController("""
            var result = new gnr.GnrBag();
            if(current_page_id && data && data.len()){
                var n = data.getNodeByAttr('_pkey',current_page_id);
                var r = n.attr;
                var profile = dojo.fromJson(r['profile']);
                var rowlist = ['nc','st','sqlc','sqlt'];
                var i,idx;
                if(!profile){
                    return;
                }
                i = 0;
                var nc = {rheader:'nc'};
                var st = {rheader:'st'};
                var sqlc = {rheader:'sqlc'};
                var sqlt = {rheader:'sqlt'};
                profile.forEach(function(p){
                        idx='v_'+i;
                        nc[idx] = p['nc']
                        st[idx] = Math.floor(p['st']*1000);
                        sqlc[idx] = p['sqlc']
                        sqlt[idx] = Math.floor(p['sqlt']*1000);
                        i++;
                });
                result.setItem('nc',null,nc);
                result.setItem('st',null,st);
                result.setItem('sqlc',null,sqlc);
                result.setItem('sqlt',null,sqlt);
            }
            SET gnr.maintenance.data.current_page_profile = result;
            """,current_page_id='^.grid.selectedId',data='^gnr.maintenance.data.pages',_if='current_page_id')
        
        profileframe = profilepane.frameGrid(frameCode='currentProfile',struct=self._profile_grid_struct,
                        datapath='.currentProfile',
                        pbl_classes=True,margin='2px',_class='pbl_roundedGroup')
        profileframe.grid.bagStore(storepath='gnr.maintenance.data.profile',storeType='AttributesBagRows',
                                sortedBy='=.grid.sorted',
                                data='^gnr.maintenance.data.current_page_profile',selfUpdate=True)
        
        profileframe.top.slotBar('2,vtitle,*',vtitle='!!Rpc details',_class='pbl_roundedGroupLabel')


        connectionframe = sc.contentPane(title='Connections').frameGrid(frameCode='currentConnections',struct=self._connection_grid_struct,
                        datapath='.currentConnections',
                        title='Connections',pbl_classes=True,margin='2px',_class='pbl_roundedGroup')
        connectionframe.grid.data('.sorted','age:d')
        connectionframe.grid.bagStore(storepath='gnr.maintenance.data.connections',storeType='AttributesBagRows',
                                sortedBy='=.grid.sorted',
                                data='^gnr.maintenance.data.loaded_connections',selfUpdate=True)
        bar = connectionframe.top.slotBar('2,vtitle,*,searchOn,2',vtitle='Connections',_class='pbl_roundedGroupLabel')



    @public_method
    def _maintenance_resetMemcached(self):
        self.site.shared_data.flush_all()

    def _page_grid_struct(self, struct):
        r = struct.view().rows()
        r.cell('register_item_id', width='14em', name='Page id',hidden=True)
        r.cell('user', width='6em', name='User')
        r.cell('user_ip', width='6em', name='User ip')
        r.cell('connection_id', width='6em', name='Connection id')

        #r.cell('start_ts', width='11em', name='Start', dtype='DH')
        r.cell('pagename', width='8em', name='Pagename')
        r.cell('age', width='6em', dtype='L', name='Conn.Time',format='DHMS')
        r.cell('last_refresh_age', width='6em', dtype='L', name='last refresh',format='DHMS')
        r.cell('last_rpc_age', width='6em', dtype='L', name='last rpc',format='DHMS')

        r.cell('last_event_age', width='6em', dtype='L', name='Last Act.',format='DHMS')
        
        r.cell('page_profile',width='9em',name='Page profile')
        
        r.cell('alive',width='4em',semaphore=True,name='Alive',dtype='B')


    def _profile_grid_struct(self, struct):
        r = struct.view().rows()
        r.cell('rheader',width='6em',name=' ')
        for i in range(20):
            r.cell('v_%i' %i,width='4em',name='T %i' %i)

    def _connection_grid_struct(self, struct):
        r = struct.view().rows()
        r.cell('register_item_id', width='14em', name='Connection id')
        r.cell('user', width='6em', name='User')
        r.cell('user_ip', width='8em', name='IP')
        
        r.cell('age', width='6em', dtype='L', name='Conn.Time',format='DHMS')
        r.cell('last_refresh_age', width='4em', dtype='L', name='L. refresh',format='DHMS')
        r.cell('last_rpc_age', width='4em', dtype='L', name='L. Rpc',format='DHMS')

        r.cell('last_event_age', width='6em', dtype='L', name='Last Act.',format='DHMS')
        r.cell('alive',width='4em',semaphore=True,name='Alive',dtype='B')
        r.cell('browser_name',dtype='T',name='Browser')

    def connected_users_struct(self,struct):
        r = struct.view().rows()
        r.cell('_checked',userSets=True,name=' ')
        r.cell('user', width='6em', name='User')
        r.cell('age', width='8em', dtype='L', name='Conn.Time',format='DHMS')
        r.cell('last_refresh_age', width='6em', dtype='L', name='last refresh',format='DHMS')
        r.cell('last_rpc_age', width='6em', dtype='L', name='last rpc',format='DHMS')
        r.cell('last_event_age', width='6em', dtype='L', name='Last Act.',format='DHMS')
        r.cell('alive',width='4em',semaphore=True,name='Alive',dtype='B')

    def btn_maintenance(self,pane,**kwargs):
        if 'superadmin' in self.userTags or '_DEV_' in self.userTags:
            pane.div(_class='button_block iframetab').div(_class='gear',tip='!!Maintenance',
                        connect_onclick="""SET left.selected='maintenance';genro.getFrameNode('standard_index').publish('showLeft');""",
                        nodeId='plugin_block_maintenance')
            
    def _maintenance_get_items(self, items, child_name=None,exclude_guest=None, **kwargs):
        result = Bag()
        now = datetime.now()

        for key, item in items.items():
            item = dict(item)
            item.pop('data',None)
            if exclude_guest and ( key.startswith('guest_') or item.get('user','').startswith('guest_')):
                continue
            _customClasses = []
            item['_pkey'] = key
            item['alive'] = True
            item['age'] = (now - item['start_ts']).seconds
            item['last_refresh_age'] = (now - item.get('last_refresh_ts',item['start_ts'])).seconds
            item['last_event_age'] = (now - item.get('last_user_ts',item['start_ts'])).seconds
            item['last_rpc_age'] = (now - item.get('last_rpc_ts',item['start_ts'])).seconds

            if item['last_refresh_age'] > 60:
                item['alive'] = False
                _customClasses.append('disconnected')
            elif item['last_event_age'] > 60:
                _customClasses.append('inactive')
           #if child_name and not item[child_name]:
           #    _customClasses.append('no_children')
            item.pop('datachanges', None)
            #if child_name is None:
            #    self.maintenance_cellServerProfile(item)
            result.setItem(key, None, _customClasses=' '.join(_customClasses), **item)
        return result


    def maintenance_cellServerProfile(self,item):
        if not item['profile']:
            return
        profiles = fromJson(item['profile'])
        result = []
        for n in profiles:
            st = n['st']
            if st==0:
                color = 'gray'
            elif st<=2:
                color = 'green'
            elif st<4:
                color = 'yellow'
            elif st<6:
                color = 'orange'
            else:
                color = 'red'
            c = dict(height=1+n['nc']/4,color=color)
            result.append('<div style="background:%(color)s;height:%(height)ipx; width:3px; display:inline-block;margin-right:1px;"></div>' %c)
        item['page_profile'] = '<div>%s</div>'  %''.join(result)


    @public_method
    def maintenance_update_data(self, exclude_guest=None,**kwargs):
        result = Bag()
        result['users'] = self._maintenance_get_items(self.site.register.users(), 'connections',exclude_guest=exclude_guest)
        connections = self.site.register.connections()
        result['connections'] = self._maintenance_get_items(connections, 'pages')
        pages = self.site.register.pages()
        result['pages'] = self._maintenance_get_items(pages,exclude_guest=exclude_guest)
        return result






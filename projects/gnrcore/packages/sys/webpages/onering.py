#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  untitled
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#
from gnr.core.gnrdecorator import public_method
from gnr.core.gnrbag import Bag
import Pyro4
from gnr.core.gnrstring import fromJson
from datetime import datetime,timedelta



class GnrCustomWebPage(object):
    css_requires='public'
    py_requires='gnrcomponents/framegrid:FrameGrid'


    def windowTitle(self):
        return '!!One Ring'

    def sitesStruct(self,struct):
        r = struct.view().rows()
        r.cell('sitename', width='10em',name='Site name')
        #r.cell('register_uri',width='20em',name='Register uri')
        #r.cell('server_uri',width='20em',name='Server uri')
        r.cell('start_ts',width='10em',name='Started',dtype='DH')
        r.cell('active',width='20px',name='S',dtype='B',semaphore=True)
        r.cell('allowed_users',width='25em',name='Allowed users')

    def main(self, root, **kwargs):
        bc = root.borderContainer(datapath='main')
        top = bc.borderContainer(region='top',height='250px',splitter=True)
        self.sitesFrame(top.contentPane(width='500px',region='left'))
        self.siteControlPane(top.framePane(region='center',gradient_from='whitesmoke',gradient_to='white',gradient_deg=90))
        self.userConnectionPages(bc.framePane(frameCode='ucp_filtered',region='center'))


    def userConnectionPages(self,frame):
        frame.css('.disconnected .dojoxGrid-cell', "color:red !important;")
        frame.css('.inactive .dojoxGrid-cell', "color:orange !important;")
        frame.css('.no_children .dojoxGrid-cell', "color:yellow !important;")
        bar = frame.top.slotToolbar('5,stackButtons,*,cleanIdle,5')
        bar.cleanIdle.button('Clean')
        sc = frame.center.stackContainer()
        self.userFrame(sc.borderContainer(title='Users',design='sidebar'))
        self.connectionFrame(sc.contentPane(title='Connections'))
        self.pagesFrame(sc.borderContainer(title='Pages'))
        
    def userFrame(self,bc):
        userframe = bc.contentPane(region='left',width='450px',splitter=True).frameGrid(frameCode='connectedUsers',struct=self.connected_users_struct,
                                                                            grid_multiSelect=False,grid_autoSelect=True,
                                                                            datapath='.connectedUsers',margin='2px',_class='pbl_roundedGroup')
        userframe.grid.data('.sorted','username:a')
        userframe.grid.bagStore(storepath='current_site.data.user',storeType='AttributesBagRows',
                                sortedBy='=.grid.sorted',
                                data='^current_site.data.loaded_users',selfUpdate=True)
        userframe.top.slotBar('2,vtitle,*,searchOn,2',vtitle='User',_class='pbl_roundedGroupLabel')
        userframe.grid.dataController("""var filteredConnection = allconnections.deepCopy()
            var cnodes = filteredConnection.getNodes();
            var n;
            for(var i =0; i<cnodes.length; i++){
                n = cnodes[i];
                if(n.attr.user!=currentUser){
                    filteredConnection.popNode(n.label);
                }
            }
            FIRE current_site.data.loaded_filtered_connections = filteredConnection;
            """,currentUser='^.selectedId',allconnections='=current_site.data.connections')


        connectionframe = bc.contentPane(region='top',height='150px',splitter=True).frameGrid(frameCode='connectionFiltered',struct=self._connection_filtered_grid_struct,
                                                                    grid_autoSelect=True,
                                                                    datapath='.connectionFiltered',margin='2px',_class='pbl_roundedGroup')

        connectionframe.grid.data('.sorted','age:d')
        connectionframe.grid.bagStore(storepath='current_site.data.filtered_connections',storeType='AttributesBagRows',
                                sortedBy='=.grid.sorted',
                                data='^current_site.data.loaded_filtered_connections',selfUpdate=True)
        connectionframe.top.slotBar('2,vtitle,*,searchOn,2',vtitle='Connections',_class='pbl_roundedGroupLabel')

        connectionframe.grid.dataController("""
            var filteredPages = allpages.deepCopy()
            var cnodes = filteredPages.getNodes();
            var n;
            for(var i =0; i<cnodes.length; i++){
                n = cnodes[i];
                if(n.attr.connection_id!=connection_id){
                    filteredPages.popNode(n.label);
                }
            }
            FIRE current_site.data.loaded_filtered_pages = filteredPages;
            """,connection_id='^.selectedId',allpages='=current_site.data.pages')
        pagesframe = bc.contentPane(region='center').frameGrid(frameCode='currentFilteredPages',struct=self._page_filtered_grid_struct,
                        datapath='.currentFilteredPages',
                        title='Pages',pbl_classes=True,margin='2px',_class='pbl_roundedGroup')
        pagesframe.grid.data('.sorted','age:d')
        pagesframe.grid.bagStore(storepath='current_site.data.filtered_pages',storeType='AttributesBagRows',
                                sortedBy='=.grid.sorted',
                                data='^current_site.data.loaded_filtered_pages',selfUpdate=True)
        pagesframe.top.slotBar('2,vtitle,*,searchOn,2',vtitle='Connected user',_class='pbl_roundedGroupLabel')


    def connectionFrame(self,pane):
        connectionframe = pane.frameGrid(frameCode='currentConnections',struct=self._connection_grid_struct,
                        datapath='.currentConnections',
                        title='Connections',pbl_classes=True,margin='2px',_class='pbl_roundedGroup')
        connectionframe.grid.data('.sorted','age:d')
        connectionframe.grid.bagStore(storepath='current_site.data.connections',storeType='AttributesBagRows',
                                sortedBy='=.grid.sorted',
                                data='^current_site.data.loaded_connections',selfUpdate=True)
        connectionframe.top.slotBar('2,vtitle,*,searchOn,2',vtitle='Connections',_class='pbl_roundedGroupLabel')

    def pagesFrame(self,bc):
        profilepane = bc.contentPane(region='bottom',height='200px')
        pagesframe = bc.contentPane(region='center').frameGrid(frameCode='currentPages',struct=self._page_grid_struct,
                        datapath='.currentPages',
                        title='Pages',pbl_classes=True,margin='2px',_class='pbl_roundedGroup')
        pagesframe.grid.data('.sorted','age:d')
        pagesframe.grid.bagStore(storepath='current_site.data.pages',storeType='AttributesBagRows',
                                sortedBy='=.grid.sorted',
                                data='^current_site.data.loaded_pages',selfUpdate=True)
        pagesframe.top.slotBar('2,vtitle,*,searchOn,2',vtitle='Connected user',_class='pbl_roundedGroupLabel')
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
            SET current_site.data.current_page_profile = result;
            """,current_page_id='^.grid.selectedId',data='^current_site.data.pages',_if='current_page_id')
        
        profileframe = profilepane.frameGrid(frameCode='currentProfile',struct=self._profile_grid_struct,
                        datapath='.currentProfile',
                        pbl_classes=True,margin='2px',_class='pbl_roundedGroup')
        profileframe.grid.bagStore(storepath='current_site.data.profile',storeType='AttributesBagRows',
                                sortedBy='=.grid.sorted',
                                data='^current_site.data.current_page_profile',selfUpdate=True)
        profileframe.top.slotBar('2,vtitle,*',vtitle='!!Rpc details',_class='pbl_roundedGroupLabel')

    def sitesFrame(self,pane):
        frame = pane.frameGrid(frameCode='runningSites',datapath='runningSites',
                   struct=self.sitesStruct,_class='pbl_roundedGroup',
                    grid_autoSelect=True,
                   grid_selected_sitename='main.selected_sitename',
                   margin='2px')
        frame.grid.bagStore(storepath='runningSites.store',storeType='AttributesBagRows',
                                sortedBy='=.grid.sorted',
                                data='^runningSites.loaded_data',selfUpdate=True)
        pane.dataController("SET main.sitename=selected_sitename;",selected_sitename='^main.selected_sitename')
        pane.dataRpc('runningSites.loaded_data',self.runningSites,_onStart=True,_timing=5)
        pane.dataRpc('dummy',self.daemonCommands,command='^runningSites.command',sitename='=main.sitename')

        frame.dataRpc('dummy',self.loadSelectedSiteSituation,
            _onResult="""SET current_site.data.loaded_users = result.popNode("users");
                         SET current_site.data.loaded_connections = result.popNode("connections");
                         SET current_site.data.loaded_pages = result.popNode("pages");
                         """,_timing=3,
            sysrpc=True,sitename='^main.sitename')
        frame.dataRpc('current_site.record',self.getSiteRecord,sitename='^main.sitename')
        frame.top.slotBar('2,vtitle,*',vtitle='Running sites',_class='pbl_roundedGroupLabel')

    def siteControlPane(self,frame):
        bar = frame.top.slotBar('10,stitle,*,pgbadger,10,stop_button,2,restart_button,2',height='30px',background='#444')
        bar.stitle.div('^current_site.record.sitename',height='30px',font_size='22px',color='white',text_align='center')
        #fb.button('dump current',fire_dump='runningSites.command')
        bar.pgbadger.button('Make Postgres report',
                            ask=dict(title='Postgres report',skipOn='Shift',
                                    fields=[dict(lbl='Since (min)',wdg='numberTextBox',name='since',default_value=180)]),
                            action="genro.publish('pgbadger_run',{since:since || 180});")
        bar.dataRpc('dummy',self.pgbadger_run,subscribe_pgbadger_run=True,_onResult="""
                                    if(result){
                                        genro.openWindow(result,'_blank',{height:'900px',width:'1000px',status:0});
                                    }else{
                                        genro.dlg.alert('Error',"Parsing log error");
                                    }            
                                    """,_lockScreen=True,timeout=0)
        bar.stop_button.button('Stop current',fire_stop='runningSites.command')
        #fb.button('load current',fire_load='runningSites.command')
        bar.restart_button.button('Restart current',fire_restart='runningSites.command')
        #fb.button('Restart All',fire_restart_all='runningSites.command',colspan=2)

        fb = frame.formbuilder(cols=2,border_spacing='3px',datapath='current_site.record',margin_top='5ex')
        fb.checkbox(value='^.maintenance',label='Maintenance',validate_onAccept="""if(userChange){
                                                                                                if(!value){
                                                                                                    SET .allowed_users = null;
                                                                                                }
                                                                                                FIRE main.setInMaintenance = value;
                                                                                         }""")
        fb.textbox(value='^.allowed_users',lbl='Allowed user',validate_onAccept="""if(userChange){
                                                                                                if(GET .maintenance){
                                                                                                    FIRE main.setInMaintenance = value;
                                                                                                }
                                                                                         }""",width='30em')

        fb.dataRpc('dummy',self.setInMaintenance,sitename='=main.sitename',status='^main.setInMaintenance',allowed_users='=.allowed_users')

    @public_method
    def pgbadger_run(self,since=None):
        pgbadger = self.site.getService('pgbadger')
        if pgbadger:
            return pgbadger.run(start_ts=datetime.now()-timedelta(minutes=since))

    @public_method
    def loadSelectedSiteSituation(self,sitename=None):
        with self.site.register.gnrdaemon_proxy.siteRegisterProxy(sitename) as register_proxy:
            result = self.maintenance_update_data(register_proxy)
            
            return result
        return Bag()

    @public_method
    def getSiteRecord(self,sitename=None):
        result = Bag()
        with self.site.register.gnrdaemon_proxy.siteRegisterProxy(sitename) as register_proxy:
            maintenance = register_proxy.isInMaintenance()
            #result.setItem('site_situation')
            result = Bag(dict(sitename=sitename,maintenance=maintenance,allowed_users=register_proxy.allowedUsers()))
        return result

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


    def _page_filtered_grid_struct(self, struct):
        r = struct.view().rows()
        r.cell('register_item_id', width='14em', name='Page id',hidden=True)
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


    def _connection_filtered_grid_struct(self, struct):
        r = struct.view().rows()
        r.cell('register_item_id', width='14em', name='Connection id')
        r.cell('age', width='6em', dtype='L', name='Conn.Time',format='DHMS')
        r.cell('last_refresh_age', width='7em', dtype='L', name='L. refresh',format='DHMS')
        r.cell('last_rpc_age', width='7em', dtype='L', name='L. Rpc',format='DHMS')
        r.cell('last_event_age', width='8em', dtype='L', name='Last Act.',format='DHMS')
        r.cell('alive',width='4em',semaphore=True,name='Alive',dtype='B')
        r.cell('browser_name',dtype='T',name='Browser')

    @public_method
    def daemonCommands(self,command=None,sitename=None):
        return getattr(self.site.register.gnrdaemon_proxy,'siteregister_%s' %command,None)(sitename)
        
    @public_method
    def setInMaintenance(self,sitename=None,status=None,allowed_users=None):
        self.site.register.gnrdaemon_proxy.setSiteInMaintenance(sitename=sitename,status=status,allowed_users=allowed_users)

   

    @public_method
    def runningSites(self):
        result = Bag()
        proxy = self.site.register.gnrdaemon_proxy
        sites = proxy.siteRegisters()
        for k, v in sites:
            v = dict(v)
            v['_pkey'] = v['sitename']
            with Pyro4.Proxy(v['register_uri']) as proxy:
                v['active'] = not proxy.isInMaintenance()
                v['allowed_users'] = proxy.allowedUsers()
            result.setItem(k,None,**v)
        return result


    def _maintenance_get_items(self, items, child_name=None,exclude_guest=None, **kwargs):
        result = Bag()
        now = datetime.now()

        for item in items:
            item = dict(item)
            key = item['register_item_id']
            item.pop('data',None)
            if exclude_guest and ( key.startswith('guest_') or item.get('user','').startswith('guest_')):
                continue
            _customClasses = []
            item['_pkey'] = key
            item['alive'] = True
            item['age'] = (now - item.get('start_ts')).seconds
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
    def maintenance_update_data(self,register_proxy, exclude_guest=None,**kwargs):
        result = Bag()
        users = register_proxy.users()
        result['users'] = self._maintenance_get_items(users, 'connections',exclude_guest=exclude_guest)
        connections = register_proxy.connections()
        result['connections'] = self._maintenance_get_items(connections, 'pages')
        pages = register_proxy.pages()
        result['pages'] = self._maintenance_get_items(pages,exclude_guest=exclude_guest)
        return result


    def connected_users_struct(self,struct):
        r = struct.view().rows()
        r.cell('user', width='6em', name='User')
        r.cell('age', width='8em', dtype='L', name='Conn.Time',format='DHMS')
        r.cell('last_refresh_age', width='6em', dtype='L', name='last refresh',format='DHMS')
        r.cell('last_rpc_age', width='6em', dtype='L', name='last rpc',format='DHMS')
        r.cell('last_event_age', width='6em', dtype='L', name='Last Act.',format='DHMS')
        r.cell('alive',width='4em',semaphore=True,name='Alive',dtype='B')

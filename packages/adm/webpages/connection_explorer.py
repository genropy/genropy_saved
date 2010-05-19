#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  untitled
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#

from gnr.core.gnrbag import Bag

class GnrCustomWebPage(object):
    maintable='adm.connection'
    py_requires='public:Public,public:IncludedView'
    subscribed_tables='adm.connection,adm.served_page'
    def pageAuthTags(self, method=None, **kwargs):
        return 'user'
        
    def windowTitle(self):
        return '!!Connection explorer'
        
    def main(self, rootBC, **kwargs):
        rootBC.data('gnr.polling',3)
        tc,top,bottom = self.pbl_rootTabContainer(rootBC,'!!Connections')
        self.overviewPane(tc.borderContainer(title='!!Overview',datapath='overviewPane'))
        self.userPane(tc.borderContainer(title='!!Users',datapath='userPane'))
        self.connectionPane(tc.borderContainer(title='!!Connections',datapath='connectionPane'))
        self.pagePane(tc.borderContainer(title='!!Pages',datapath='pagesPane'))
        
    def overviewPane(self,bc):
        bc.dataRpc(".total_connection", "countConnections",_fired='^gnr.dbevent.adm_connection',_onStart=True)
        bc.dataRpc(".total_served_page", "countServedPages",_fired='^gnr.dbevent.adm_served_page',_onStart=True)

        pane = bc.contentPane(region='center')
        fb = pane.formbuilder(cols=1, border_spacing='4px')
        fb.div('^.total_connection',lbl='!!Total active connections')
        fb.div('^.total_served_page',lbl='!!Total active served pages')

        
    def rpc_countConnections(self):
        return self.db.table('adm.connection').query(where='$end_ts IS NULL').count()
        
    def rpc_countServedPages(self):
        return self.db.table('adm.served_page').query(where='$end_ts IS NULL').count()
        
    def connectionPane(self,bc):
        def label(pane,**kwargs):
            pane.checkbox(value='^.activeOnly',label='!!Only active connections')
        bc.dataFormula(".connections.activeOnly", True,_onStart=True)
        tools_menu = Bag()
        tools_menu.setItem('reload',None,caption='Reload',action='FIRE .reload')
        tools_menu.setItem('send_message',None,caption='Send Message',action='FIRE .send_message')
        tools_menu.setItem('-',None,caption='-')
        tools_menu.setItem('clear',None,caption='Clear expired',action='FIRE .clear_expired')
        bc.data(".connections.tools_menu", tools_menu)
        bc.dataRpc('dummy','clearExpiredConnections',_fired='^.connections.clear_expired')
        
        self.includedViewBox(bc,label=label,datapath='.connections',
                             nodeId='connectionMainGrid',table='adm.connection',autoWidth=True,
                             struct=self.connectionMainGrid_struct,filterOn='!!User:username,End reason:end_reason',
                             reloader='^.activeOnly', externalChanges=True,tools_menu=".tools_menu",
                             selectionPars=dict(where='($end_ts IS NULL AND :activeOnly) OR ($end_ts IS NOT NULL AND NOT :activeOnly)',
                             activeOnly='=.activeOnly',order_by='$start_ts DESC'))
                             
                             
    def rpc_clearExpiredConnections(self):
        self.site.clearExpiredConnections()
        
    def connectionMainGrid_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('username', name='User', width='12em')
        r.fieldcell('start_ts')
        r.fieldcell('end_ts')
        r.fieldcell('end_reason')
        r.fieldcell('ip')
        return struct
        
        
    def pagePane(self,bc):
        def label(pane,**kwargs):
            pane.checkbox(value='^.activeOnly',label='!!Only active served pages')
        bc.dataFormula(".connections.activeOnly", True,_onStart=True)
        self.includedViewBox(bc,label=label,datapath='.connections',tools_menu=self.toolsMenu(bc,'pagesMainGrid'),
                             nodeId='pagesMainGrid',table='adm.served_page',autoWidth=True,
                             struct=self.servedPages_struct,filterOn='Username:@connection_id.username,Page:pagename,End reason:end_reason',
                             reloader='^.activeOnly', externalChanges=True,
                             selectionPars=dict(where='($end_ts IS NULL AND :activeOnly) OR ($end_ts IS NOT NULL AND NOT :activeOnly)',
                             activeOnly='=.activeOnly',order_by='$start_ts DESC'))
                             
    def servedPages_struct(self,struct):
        r = struct.view().rows()
        r.cell('page_id',name='Served Page ID',width='20em')
        r.cell('@connection_id.username',name='Username',width='15em')
        r.cell('pagename',name='Page name',width='15em')
        r.cell('start_ts',name='Start',dtype='DH',width='10em')
        r.cell('end_ts',name='End',dtype='DH',width='10em')
        r.cell('end_reason',name='End reason',width='10em')
        return struct       
                
        
    def userPane(self,bc):
        topBC = bc.borderContainer(region='top',height='50%')
        self.connectedUser(topBC.borderContainer(region='left',width='50%',margin='5px'))
        self.userConnections(topBC.borderContainer(region='center',margin_left=0,margin='5px'))
        centerBC = bc.borderContainer(region='center',margin='5px',margin_top=0)
        self.userServedPages(centerBC)

    def connectedUser(self,bc):
       #topfb=bc.contentPane(region='top',height='40px', datapath='messages.user').formBuilder(cols='3')
       #topfb.textBox(value='^.text',lbl='User message',width='15em')
       #topfb.button('send',lbl='',fire='.send')
       #topfb.button('refresh',lbl='',fire="users.reload")
       #topfb.dataRpc('.result','sendMessage',_fired='^.send', msg='=.text', 
       #              dest_user='=users.selectedId?username')
       #bc=bc.borderContainer(region='center')
        self.includedViewBox(bc,table='adm.connection',
                            nodeId='connected_users',tools_menu=self.toolsMenu(bc,'connected_users'),
                            datapath='.users',
                            label='!!Live user connected',
                            struct=self._connectedUser_struct, 
                            autoWidth=True,autoSelect=True,
                            externalChanges=True,
                            selectionPars=dict(where='$end_ts IS NULL',distinct=True,
                                                applymethod='createUserUniqueIdentifier',
                                                _onStart=True))


    def rpc_createUserUniqueIdentifier(self,selection):
        def createPkey(row):         
            result= dict(pkey ='%s.%s' %(row['username'],row['ip'])) 
            return result
        selection.apply(createPkey)  
                      
    def _connectedUser_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('username',width='10em')
        r.fieldcell('user_fullname', width='10em')
        r.fieldcell('ip', name='Remote addr.', width='15em')
        return struct
        
    def userConnections(self,bc):
       #topfb=bc.contentPane(region='top',height='40px',datapath='messages.connection').formBuilder(cols='3')
       #topfb.textBox(value='^.text',lbl='Connection message',width='15em')
       #topfb.button('send',lbl='',fire='.send')
       #topfb.button('refresh',lbl='',fire="connections.reload")
       #topfb.dataRpc('.result','sendMessage',_fired='^.send', msg='=.text', dest_connection='=connection.current')
       #bc=bc.borderContainer(region='center')
        
        self.includedViewBox(bc,nodeId='user_connections',datapath='.connections',table='adm.connection',
                            struct=self._userConnections_struct, tools_menu=self.toolsMenu(bc,'user_connections'),
                            autoWidth=True,label='!!User connections',
                            reloader='^userPane.users.selectedId',autoSelect=True,
                            selectionPars=dict(where='$end_ts IS NULL AND $username=:user AND $ip=:ip',
                                                user='=userPane.users.selectedId?username',
                                                ip='=userPane.users.selectedId?ip'))
    def toolsMenu(self,pane,gridId):
        tools_menu = Bag()
        tools_menu.setItem('reload',None,caption='Reload',action='FIRE .reload')
        tools_menu.setItem('send_message',None,caption='Send Message',action='FIRE .send_message')
        pane.data('#%s.tools_menu' %gridId,tools_menu)
        return '.tools_menu'

    def _userConnections_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('start_ts',width='8em')
        r.fieldcell('user_agent', width='35em')
        return struct
        
    def userServedPages(self,bc):
        #topfb=bc.contentPane(region='top',height='40px', datapath='messages.pages').formBuilder(cols='3')
        #topfb.textBox(value='^.text',lbl='Page message',width='30em')
        #topfb.button('send',lbl='',fire='.send')
        #topfb.button('refresh',lbl='',fire="pages.reload")
        #
        #topfb.dataRpc('.result','sendMessage',_fired='^.send', msg='=.text', dest_page='=pages.selectedId')
        #bc=bc.borderContainer(region='center')
        #bc.dataController("console.log(selectedId)",selectedId="^connections.selectedId")
        
        self.includedViewBox(bc,label='!!User served pages',table='adm.served_page', 
                            struct=self._userServedPages_struct, autoWidth=True,
                           nodeId='user_servedpages',autoSelect=True,tools_menu=self.toolsMenu(bc,'user_servedpages'),
                           datapath='.pages',
                           externalChanges='connection_id=userPane.connections.selectedId:UID',
                           reloader='^userPane.connections.selectedId',
                           selectionPars=dict(where='$connection_id=:connection_id AND $end_ts IS NULL',
                                                connection_id='=userPane.connections.selectedId',
                                                order_by='$start_ts desc',_if='connection_id'))
                           

                         
    def _userServedPages_struct(self,struct):
        r = struct.view().rows()
        r.cell('page_id',name='Served Page ID',width='20em')
        r.cell('start_ts',name='Start',dtype='DH',width='10em')
        r.cell('end_ts',name='End',dtype='DH',width='10em')
        r.cell('end_reason',name='End reason',width='10em')
        r.cell('pagename',name='Page name',width='15em')
        return struct
        
    def rpc_sendMessage(self,msg=None, dest_user=None, dest_connection=None, dest_page=None):
        """
        user and connection_id are mutually exclusive
        """
        if dest_user:
            mode='user'
        elif dest_connection:
            mode='connection'
        elif dest_page:
            mode='page'
        else:
            mode='missing'
        print dest_user, ',', dest_connection, ',', dest_page
        print mode, msg
        if ':' in msg:
            message_type, msg = msg.split(':',1)
        else:
            message_type = 'servermsg'
        self.site.writeMessage(body=Bag({message_type:msg}) ,user=dest_user, page_id=dest_page, 
                               connection_id=dest_connection, message_type=message_type)
        self.db.commit()
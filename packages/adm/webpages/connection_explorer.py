#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  untitled
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#

# --------------------------- GnrWebPage subclass ---------------------------
from gnr.core.gnrbag import Bag

class GnrCustomWebPage(object):
    maintable='adm.connection'
    py_requires='public:Public,public:IncludedView'
    
    pageOptions=dict(subscribed_tables='adm.connection,adm.served_page')
    
    def pageAuthTags(self, method=None, **kwargs):
        return 'user'
        
    def windowTitle(self):
        return '!!Connection explorer'
        
    def main(self, rootBC, **kwargs):
        rootBC.data('gnr.polling',3)
        bc,top,bottom = self.pbl_rootBorderContainer(rootBC,'!!Connections')
        topBC = bc.borderContainer(region='top',height='50%')
        self.connectedUser(topBC.borderContainer(region='left',width='50%',margin='5px'))
        self.userConnections(topBC.borderContainer(region='center',margin_left=0,margin='5px'))
        centerBC = bc.borderContainer(region='center',margin='5px',margin_top=0)
        self.userServedPages(centerBC)
        self.gridControllers(rootBC)
        
    def gridControllers(self,pane):
       pane.dataController( """genro.wdgById('connected_users').reload(true);
                             if((username==current_user)&&(userip==current_ip)){
                                 genro.wdgById('user_connections').reload(true);
                             }""",
                             dbevent='=gnr.dbevent.adm_connection?dbevent',
                             current_user='=user.current.name',
                             current_ip='=user.current.ip',
                             userip='=gnr.dbevent.adm_connection.ip',
                             username='=gnr.dbevent.adm_connection.username',
                             _fired='^gnr.dbevent.adm_connection')
                             
       pane.dataController( """
                              console.log('cambiato pagina')
                              if (connection_id==current_connection){
                                    console.log('riga corrente connessioni')
                                   genro.wdgById('user_servedpages').reload(true);
                              }else{
                                   console.log('current_connection:'+current_connection+' connection_id:'+connection_id+' dbevent:'+dbevent)
                              }""",
                             dbevent='=gnr.dbevent.adm_served_page?dbevent',
                             current_connection='=connection.current',
                             connection_id='=gnr.dbevent.adm_served_page.connection_id',
                             _fired='^gnr.dbevent.adm_served_page')

    def connectedUser(self,bc):
        topfb=bc.contentPane(region='top',height='40px', datapath='messages.user').formBuilder(cols='3')
        topfb.textBox(value='^.text',lbl='User message',width='15em')
        topfb.button('send',lbl='',fire='.send')
        #topfb.button('refresh',lbl='',action="genro.wdgById('connected_users').reload(true)")
        topfb.button('refresh',lbl='',fire="grids.connected_users.reload")
        topfb.dataRpc('.result','sendMessage',_fired='^.send', msg='=.text', 
                      dest_user='=grids.connected_user.selectedId?username')
        bc=bc.borderContainer(region='center')
        self.includedViewBox(bc,table='adm.connection',
                            nodeId='connected_users',
                            label='!!Live user connected',
                            struct=self._connectedUser_struct, 
                            autoWidth=True,autoSelect=True,
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
        topfb=bc.contentPane(region='top',height='40px',datapath='messages.connection').formBuilder(cols='3')
        topfb.textBox(value='^.text',lbl='Connection message',width='15em')
        topfb.button('send',lbl='',fire='.send')
        topfb.button('refresh',lbl='',fire="grids.user_connections.reload")
        topfb.dataRpc('.result','sendMessage',_fired='^.send', msg='=.text', dest_connection='=connection.current')
        bc=bc.borderContainer(region='center')
        self.includedViewBox(bc,label='!!User connections',
                            table='adm.connection',
                            struct=self._userConnections_struct, 
                            autoWidth=True,nodeId='user_connections',autoSelect=True,
                            reloader='^grids.connected_users.selectedId',
                            selectionPars=dict(where='$end_ts IS NULL AND $username=:user AND $ip=:ip',
                                                user='=grids.connected_users.selectedId?username',
                                                ip='=grids.connected_users.selectedId?ip'))

    def _userConnections_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('start_ts',width='15em')
        r.fieldcell('user_agent', width='15em')
        return struct
        
    def userServedPages(self,bc):
        topfb=bc.contentPane(region='top',height='40px', datapath='messages.pages').formBuilder(cols='3')
        topfb.textBox(value='^.text',lbl='Page message',width='30em')
        topfb.button('send',lbl='',fire='.send')
        topfb.button('refresh',lbl='',fire="grids.user_servedpages.reload")
        
        topfb.dataRpc('.result','sendMessage',_fired='^.send', msg='=.text', dest_page='=grids.user_servedpages.selectedId')
        bc=bc.borderContainer(region='center')
        self.includedViewBox(bc,label='!!User served pages',table='adm.served_page', 
                            struct=self._userServedPages_struct, autoWidth=True,
                           nodeId='user_servedpages',autoSelect=True,
                           reloader='^grids.user_connections.selectedId',
                           selectionPars=dict(where='$connection_id=:conn_id',
                                                conn_id='=grids.user_connections.selectedId',
                                                order_by='$start_ts desc'))
                           

                         
    def _userServedPages_struct(self,struct):
        r = struct.view().rows()
        r.cell('page_id',name='Served Page ID',width='20em')
        r.cell('start_ts',name='Start',dtype='DH',width='10em')
        r.cell('end_ts',name='End',dtype='DH',width='10em')
        r.cell('end_reason',name='End reason',width='10em')
        r.cell('pagename',name='Page name',width='15em')
        r.cell('subscribed_tables',name='Subscribed table',width='20em')
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
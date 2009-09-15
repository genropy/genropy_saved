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
        self.connectedUser(topBC.borderContainer(region='left',width='50%',margin='5px', datapath='user'))
        self.userConnections(topBC.borderContainer(region='center',margin_left=0,margin='5px',datapath='connection'))
        centerBC = bc.borderContainer(region='center',margin='5px',margin_top=0, datapath='page')
        self.userServedPages(centerBC)
        
    def connectedUser(self,bc):
        topfb=bc.contentPane(region='top',height='40px', datapath='.messages').formBuilder(cols='3')
        topfb.textBox(value='^.text',lbl='User message',width='15em')
        topfb.button('send',lbl='',fire='.send')
        #topfb.button('refresh',lbl='',fire='user.refresh')
        topfb.button('refresh',lbl='',action="genro.wdgById('connected_users').reload(true)")

        topfb.dataRpc('.result','sendMessage',_fired='^.send', msg='=.text', dest_user='=user.current')
        bc=bc.borderContainer(region='center')
        self.includedViewBox(bc,label='!!Live user connected',
                            storepath='.selection', 
                            struct=self._connectedUser_struct(), 
                            autoWidth=True,selected_username='.current',
                            nodeId='connected_users')
        bc.dataSelection('.selection','adm.connection',nodeId='connected_users_selection',
                         where='$end_ts IS NULL',distinct=True,applymethod='createUserUniqueIdentifier',
                         columns='$username,@userid.fullname,$ip',_onStart=True, #_fired='^.refresh',
                         _onResult="genro.wdgById('connected_users').loadedData()")
        bc.dataController( """console.log('update user');genro.wdgById('connected_users').reload(true)""",
                              dbevent='^gnr.dbevent.adm.connection')
    def rpc_createUserUniqueIdentifier(self,selection):
        def createPkey(row):         
            result= dict(pkey ='%s.%s' %(row['username'],row['ip'])) 
            print result
            return result
        selection.apply(createPkey)  
                      
    def _connectedUser_struct(self):
        struct = self.newGridStruct()
        r = struct.view().rows()
        r.cell('username', name='User', width='10em')
        r.cell('user_fullname', name='User fullname', width='10')
        r.cell('ip', name='Remote addr.', width='15em')
        return struct
        
    
    def userConnections(self,bc):
        topfb=bc.contentPane(region='top',height='40px', datapath='.messages').formBuilder(cols='3')
        topfb.textBox(value='^.text',lbl='Connection message',width='15em')
        topfb.button('send',lbl='',fire='.send')
        topfb.button('refresh',lbl='',fire='connection.refresh')
        
        topfb.dataRpc('.result','sendMessage',_fired='^.send', msg='=.text', dest_connection='=connection.current')
        
        bc=bc.borderContainer(region='center')
        self.includedViewBox(bc,label='!!User connections',
                            storepath='.selection', 
                            struct=self._userConnections_struct(), 
                            autoWidth=True,selectedId='.current',
                            nodeId='user_connections')
        bc.dataSelection('.selection','adm.connection',
                         where='$end_ts IS NULL AND username=:user',
                         user='^user.current',
                         columnsFromView='user_connections', _fired='^.refresh')
                         
    def _userConnections_struct(self):
        struct = self.newGridStruct()
        r = struct.view().rows()
        r.cell('start_ts', name='Start',dtype='DH', width='15em')
        r.cell('user_agent', name='User agent', width='15em')
        return struct
        
    def userServedPages(self,bc):
        topfb=bc.contentPane(region='top',height='40px', datapath='.messages').formBuilder(cols='3')
        topfb.textBox(value='^.text',lbl='Page message',width='30em')
        topfb.button('send',lbl='',fire='.send')
        topfb.button('refresh',lbl='',fire='page.refresh')
        
        topfb.dataRpc('.result','sendMessage',_fired='^.send', msg='=.text', dest_page='=page.current')
        bc=bc.borderContainer(region='center')
        self.includedViewBox(bc,label='!!User served pages',
                            storepath='.selection', 
                            struct=self._userServedPages_struct(), 
                            autoWidth=True,selectedId='.current',
                           nodeId='user_servedpages')
        bc.dataSelection('.selection','adm.served_page',
                         where='connection_id=:connection',
                         connection='^connection.current',
                         columnsFromView='user_servedpages', _fired='^.refresh')
                         
    def _userServedPages_struct(self):
        struct = self.newGridStruct()
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
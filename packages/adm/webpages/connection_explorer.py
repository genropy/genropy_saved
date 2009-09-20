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

    def connectedUser(self,bc):
        topfb=bc.contentPane(region='top',height='40px', datapath='messages.user').formBuilder(cols='3')
        topfb.textBox(value='^.text',lbl='User message',width='15em')
        topfb.button('send',lbl='',fire='.send')
        topfb.button('refresh',lbl='',fire="users.reload")
        topfb.dataRpc('.result','sendMessage',_fired='^.send', msg='=.text', 
                      dest_user='=users.selectedId?username')
        bc=bc.borderContainer(region='center')
        self.includedViewBox(bc,table='adm.connection',
                            nodeId='connected_users',
                            datapath='users',
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
        topfb=bc.contentPane(region='top',height='40px',datapath='messages.connection').formBuilder(cols='3')
        topfb.textBox(value='^.text',lbl='Connection message',width='15em')
        topfb.button('send',lbl='',fire='.send')
        topfb.button('refresh',lbl='',fire="connections.reload")
        topfb.dataRpc('.result','sendMessage',_fired='^.send', msg='=.text', dest_connection='=connection.current')
        bc=bc.borderContainer(region='center')
        self.includedViewBox(bc,nodeId='user_connections',datapath='connections',table='adm.connection',
                            struct=self._userConnections_struct, 
                            autoWidth=True,label='!!User connections',
                            reloader='^users.selectedId',autoSelect=True,
                            selectionPars=dict(where='$end_ts IS NULL AND $username=:user AND $ip=:ip',
                                                user='=users.selectedId?username',
                                                ip='=users.selectedId?ip'))

    def _userConnections_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('start_ts',width='8em')
        r.fieldcell('user_agent', width='35em')
        return struct
        
    def userServedPages(self,bc):
        topfb=bc.contentPane(region='top',height='40px', datapath='messages.pages').formBuilder(cols='3')
        topfb.textBox(value='^.text',lbl='Page message',width='30em')
        topfb.button('send',lbl='',fire='.send')
        topfb.button('refresh',lbl='',fire="pages.reload")
        
        topfb.dataRpc('.result','sendMessage',_fired='^.send', msg='=.text', dest_page='=pages.selectedId')
        bc=bc.borderContainer(region='center')
        self.includedViewBox(bc,label='!!User served pages',table='adm.served_page', 
                            struct=self._userServedPages_struct, autoWidth=True,
                           nodeId='user_servedpages',autoSelect=True,
                           datapath='pages',
                           externalChanges='connection_id=connections.selectedId:UID',
                           reloader='^connections.selectedId',
                           selectionPars=dict(where='$connection_id=:connection_id AND $end_ts IS NULL',
                                                connection_id='=connections.selectedId',
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
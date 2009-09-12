#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  untitled
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#

# --------------------------- GnrWebPage subclass ---------------------------
class GnrCustomWebPage(object):
    maintable='adm.connection'
    py_requires='public:Public,public:IncludedView'
    def pageAuthTags(self, method=None, **kwargs):
        return 'user'
        
    def windowTitle(self):
        return '!!Connection explorer'

    def main(self, rootBC, **kwargs):
        bc,top,bottom = self.pbl_rootBorderContainer(rootBC,'!!Connections')
        topBC = bc.borderContainer(region='top',height='50%')
        self.connectedUser(topBC.borderContainer(region='left',width='50%',margin='5px'))
        self.userConnections(topBC.borderContainer(region='center',margin_left=0,margin='5px'))
        centerBC = bc.borderContainer(region='center',margin='5px',margin_top=0)
        self.userSevedPages(centerBC)
        
    def connectedUser(self,bc):
        self.includedViewBox(bc,label='!!Live user connected',
                            storepath='selection.connectedUsers', 
                            struct=self._connectedUser_struct(), 
                            autoWidth=True,selected_username='current.user',
                            nodeId='connected_users')
        bc.dataSelection('selection.connectedUsers','adm.connection',
                         where='$end_ts IS NULL',distinct=True,
                         columns='$username,@userid.fullname,$ip',_onStart=True)
                            
    def _connectedUser_struct(self):
        struct = self.newGridStruct()
        r = struct.view().rows()
        r.cell('username', name='User', width='10em')
        r.cell('user_fullname', name='User fullname', width='10')
        r.cell('ip', name='Remote addr.', width='15em')
        return struct
        
    def userConnections(self,bc):
        self.includedViewBox(bc,label='!!User connections',
                            storepath='selection.userConnections', 
                            struct=self._userConnections_struct(), 
                            autoWidth=True,selectedId='current.connection',
                            nodeId='user_connections')
        bc.dataSelection('selection.userConnections','adm.connection',
                         where='$end_ts IS NULL AND username=:user',
                         user='^current.user',
                         columnsFromView='user_connections')
                         
    def _userConnections_struct(self):
        struct = self.newGridStruct()
        r = struct.view().rows()
        r.cell('start_ts', name='Start',dtype='DH', width='15em')
        r.cell('user_agent', name='User agent', width='15em')
        return struct
        
    def userSevedPages(self,bc):
        self.includedViewBox(bc,label='!!User served pages',
                            storepath='selection.servedPage', 
                            struct=self._userSevedPages_struct(), 
                            autoWidth=True,selectedId='current.servedPage',
                           nodeId='user_servedpages')
        bc.dataSelection('selection.servedPage','adm.served_page',
                         where='connection_id=:connection',
                         connection='^current.connection',
                         columnsFromView='user_servedpages')
                         
    def _userSevedPages_struct(self):
        struct = self.newGridStruct()
        r = struct.view().rows()
        r.cell('page_id',name='Served Page ID',width='20em')
        r.cell('start_ts',name='Start',dtype='DH',width='10em')
        r.cell('end_ts',name='End',dtype='DH',width='10em')
        r.cell('pagename',name='Page name',width='15em')
        r.cell('subscribed_tables',name='Subscribed table',width='20em')
        return struct
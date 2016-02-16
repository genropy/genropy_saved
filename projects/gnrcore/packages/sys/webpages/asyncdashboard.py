# -*- coding: UTF-8 -*-

class GnrCustomWebPage(object):
    py_requires = 'public:Public,gnrcomponents/framegrid:FrameGrid'
    auth_main = 'user'

    def main(self,root,**kwargs):
        bc = root.borderContainer(datapath='main')
        top = bc.borderContainer(height='200px',region='top')
        #top.roundedGroupFrame(title='Pages',region='left',width='50%').quickgrid(value='^.data.pages',fields='user,connection_id,page_id')
        #top.roundedGroupFrame(title='Shared Objects',region='center').quickgrid(value='^.data.sharedObjects',fields='subscribed_pages')
        tc = bc.tabContainer(region='center')
        bc.data('main.data',None,shared_id='__global_status__')
        self.globalStatusPane(tc.borderContainer(title='Global Status'))
        self.sharedObjectsPane(tc.contentPane(title='SharedObjects'))
        
    def globalStatusPane(self,bc):        
        
        bc.tree(storepath='.data')
        bc.dataController("""SET .selectedConnection = null;
                             SET .currentConnections= selectedUser?'main.data.users.'+selectedUser+'.connections':'emptyConnections';
        """,selectedUser='^.selectedUser')

        bc.dataController("""SET .currentPages = selectedUser&&selectedConnection?'main.data.users.'+selectedUser+'.connections.'+selectedConnection+'.pages':'emptyPages';
        """,selectedUser='=.selectedUser',selectedConnection='^.selectedConnection')

        bc.bagGrid(title='Users',region='left',width='300px', splitter=True, pbl_classes=True,addrow=False,delrow=False,
                            datapath='.usersgrid',
                            storepath='main.data.users',
                            grid_selectedLabel='main.selectedUser',
                            grid_autoSelect=True,
                            struct=self.usersStruct,margin='2px')
        right=bc.borderContainer(region='center')

        right.bagGrid(title='Connections',region='top',splitter=True, pbl_classes=True,addrow=False,delrow=False,
                                        height='180px',
                                        storepath='^main.currentConnections',
                                        datapath='.connectionsgrid',
                                        grid_autoSelect=True,
                                        grid_selectedLabel='main.selectedConnection',
                                        struct=self.connectionStruct,margin='2px')

        right.bagGrid(title='Pages',region='center',pbl_classes=True,addrow=False,delrow=False,
                                datapath='.pagessgrid',
                                storepath='^main.currentPages',
                                struct=self.pagesStruct,margin='2px')

    def usersStruct(self,struct):
        r = struct.view().rows()
        r.cell('user',width='10em',name='User')
        r.cell('start_ts',width='10em',name='Start',dtype='DH')
        r.cell('lastEventAge',width='6em',name='lastEvtAge',dtype='N')

    def connectionStruct(self,struct):
        r = struct.view().rows()
        r.cell('connection_id',width='10em',name='Connection')
        r.cell('start_ts',width='10em',name='Start',dtype='DH')
        r.cell('lastEventAge',width='6em',name='lastEvtAge',dtype='N')
        r.cell('user_ip',width='7em',name='IP')
        r.cell('user_agent',width='100%',name='User Agent')


    def pagesStruct(self,struct):
        r = struct.view().rows()
        r.cell('pagename',width='10em',name='Page')
        r.cell('start_ts',width='10em',name='Start',dtype='DH')
        r.cell('lastEventAge',width='6em',name='lastEvtAge',dtype='N')
        r.cell('typing',width='6em',name='Typing',dtype='B')
        r.cell('evt_type',width='7em',name='Evt.Type')
        r.cell('evt_timeStamp',width='10em',name='Timestamp')
        r.cell('evt_targetId',width='20em',name='Target ID')
        r.cell('evt_x',width='5em',name='x')
        r.cell('evt_y',width='5em',name='y')
        r.cell('evt_modifiers',width='8em',name='Modifiers')
        r.cell('evt_keyCode',width='6em',name='keyCode')
        r.cell('evt_keyChar',width='6em',name='keyChar')

    def sharedObjectsPane(self,pane):
        pane.bagGrid(title='Shared Objects', pbl_classes=True,addrow=False,delrow=False,
                                        storepath='main.data.sharedObjects',
                                        datapath='.sharedobjects_grid',
                                        grid_autoSelect=True,
                                        struct=self.sharedObjectStruct,margin='2px')

    def sharedObjectStruct(self,struct):
        r = struct.view().rows()
        r.cell('shared_id',width='10em',name='Shared Id')
        r.cell('expire',width='10em',name='Expire')
        r.cell('read_tags',width='10em',name='Read Tags')
        r.cell('write_tags',width='10em',name='Write Tags')
        r.cell('saveIterval',width='10em',name='Save Iterval')
        r.cell('autoSave',width='10em',name='Auto Save',dtype='B')
        r.cell('autoLoad',width='10em',name='Auto Load',dtype='B')
        r.cell('filepath',width='10em',name='Filepath')
        r.cell('subscriptions',width='100%',name='Subscriptions',dtype='X',format_bag_cells='page_id,user',format_bag_headers='Page Id,User')
        
        
   #@websocket_method
   #def getInfo(self,**kwargs):
   #    users = self.getUsers()
   #    return Bag(dict(pages=self.getPages(),sharedObjects= self.getSharedObjects(),users=users))

   #def getPages(self):
   #    pages = self.asyncServer.pages
   #    b=Bag()
   #    for page_id,page in pages.items():
   #        kw = dict([(key,getattr(page,key,None)) for key in ('page_id','connection_id','user')])
   #        b.setItem(page_id,None,**kw)
   #    return b

   #def getSharedObjects(self):
   #    return self.asyncServer.som.getUserBag()

    #def getUsers(self):
    #    result = Bag()
    #    users = self.asyncServer.users
    #    for user,userdict in users.items():
    #        connections = Bag()
    #        result.setItem(user, connections, start_ts=userdict['start_ts'],user=user)
    #        for connection_id,connectiondict in userdict['connections'].items():
    #            pages = Bag()
    #            connections.setItem(connection_id, pages, connection_id=connection_id,
    #                                user_ip=connectiondict['user_ip'],
    #                                start_ts=connectiondict['start_ts'])
    #            for page_id,page in connectiondict['pages'].items():
    #                kw = dict([(key,getattr(page,key,None)) for key in ('page_id','connection_id','user')])
    #                pages.setItem(page_id,None,**kw)
    #    return result




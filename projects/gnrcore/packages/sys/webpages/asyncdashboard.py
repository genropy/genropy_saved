# -*- coding: UTF-8 -*-

class GnrCustomWebPage(object):
    py_requires = 'public:Public,gnrcomponents/framegrid:FrameGrid'
    auth_main = 'user'

    def main(self,root,**kwargs):
        bc = root.borderContainer(datapath='main')
        top = bc.borderContainer(height='50%',region='top')
        top.contentPane(region='top').button('Run',fire='run')
        #top.roundedGroupFrame(title='Pages',region='left',width='50%').quickgrid(value='^.data.pages',fields='user,connection_id,page_id')
        #top.roundedGroupFrame(title='Shared Objects',region='center').quickgrid(value='^.data.sharedObjects',fields='subscribed_pages')
        
        center = bc.borderContainer(region='center')
        center.data('.data',None,shared_id='__global_status__')
        center.tree(storepath='.data')
        bc.dataController("""SET .selectedConnection = null;
                             SET .currentConnections= selectedUser?'main.data.users.'+selectedUser+'.connections':'emptyConnections';
        """,selectedUser='^.selectedUser')

        bc.dataController("""SET .currentPages = selectedUser&&selectedConnection?'main.data.users.'+selectedUser+'.connections.'+selectedConnection+'.pages':'emptyPages';
        """,selectedUser='=.selectedUser',selectedConnection='^.selectedConnection')

        center.bagGrid(title='Users',region='left',width='30%',pbl_classes=True,addrow=False,delrow=False,
                            datapath='.usersgrid',
                            storepath='main.data.users',
                            grid_selectedLabel='main.selectedUser',
                            grid_autoSelect=True,
                            struct=self.usersStruct,margin='2px')

        center.bagGrid(title='Connections',region='center',pbl_classes=True,addrow=False,delrow=False,
                                        storepath='^main.currentConnections',
                                        datapath='.connectionsgrid',
                                        grid_autoSelect=True,
                                        grid_selectedLabel='main.selectedConnection',
                                        struct=self.connectionStruct,margin='2px')

        center.bagGrid(title='Pages',region='right',width='20%',pbl_classes=True,addrow=False,delrow=False,
                                datapath='.pagessgrid',
                                storepath='^main.currentPages',
                                struct=self.pagesStruct,margin='2px')

    def usersStruct(self,struct):
        r = struct.view().rows()
        r.cell('user',width='10em',name='User')
        r.cell('start_ts',width='10em',name='Start',dtype='DH')

    def connectionStruct(self,struct):
        r = struct.view().rows()
        r.cell('connection_id',width='15em',name='Connection')
        r.cell('start_ts',width='10em',name='Start',dtype='DH')
        r.cell('user_ip',width='15em',name='IP')

    def pagesStruct(self,struct):
        r = struct.view().rows()
        r.cell('pagename',width='15em',name='Page')


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




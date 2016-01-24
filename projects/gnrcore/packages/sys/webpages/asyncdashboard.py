# -*- coding: UTF-8 -*-
from gnr.core.gnrdecorator import websocket_method
from gnr.core.gnrbag import Bag

class GnrCustomWebPage(object):
    py_requires = 'public:Public,gnrcomponents/framegrid:FrameGrid'
    auth_main = 'user'

    def main(self,root,**kwargs):
        bc = root.borderContainer(datapath='main')
        bc.dataRpc('.data', self.getInfo,httpMethod='WSK',_fired='^run',_timing=2)
        top = bc.borderContainer(height='50%',region='top')
        top.contentPane(region='top').button('Run',fire='run')
        top.roundedGroupFrame(title='Pages',region='left',width='50%').quickgrid(value='^.data.pages',fields='user,connection_id,page_id')
        top.roundedGroupFrame(title='Shared Objects',region='center').quickgrid(value='^.data.sharedObjects',fields='subscribed_pages')
        center = bc.borderContainer(region='center')

        bc.dataController("""
                SET .currentConnections = selectedUser?'main.data.users.'+selectedUser:'emptyConnections';
                SET .currentPages = selectedUser&&selectedConnection?'main.data.users.'+selectedUser+'.'+selectedConnection:'emptyPages';

            """,selectedConnection='^.selectedConnection',selectedUser='^.selectedUser',_delay=1)
        center.bagGrid(title='Users',region='left',width='30%',pbl_classes=True,addrow=False,delrow=False,
                            datapath='.usersgrid',
                            storepath='main.data.users',
                            grid_selectedLabel='main.selectedUser',
                            grid_autoSelect=True,
                            datamode='attr',
                            struct=self.usersStruct,margin='2px')

        center.bagGrid(title='Connections',region='center',pbl_classes=True,addrow=False,delrow=False,
                                        storepath='^main.currentConnections',
                                        datapath='.connectionsgrid',
                                        grid_autoSelect=True,
                                        grid_selectedLabel='main.selectedConnection',
                                        datamode='attr',
                                        struct=self.connectionStruct,margin='2px')

        center.bagGrid(title='Pages',region='right',width='20%',pbl_classes=True,addrow=False,delrow=False,
                                datapath='.pagessgrid',
                                storepath='^main.currentPages',
                                datamode='attr',
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
        r.cell('page_id',width='15em',name='Page')


    @websocket_method
    def getInfo(self,**kwargs):
        users = self.getUsers()
        return Bag(dict(pages=self.getPages(),sharedObjects= self.getSharedObjects(),users=users))

    def getPages(self):
        pages = self.asyncServer.pages
        b=Bag()
        for page_id,page in pages.items():
            kw = dict([(key,getattr(page,key,None)) for key in ('page_id','connection_id','user')])
            b.setItem(page_id,None,**kw)
        return b

    def getSharedObjects(self):
        sharedObjects= self.asyncServer.sharedObjects
        pages = self.asyncServer.pages
        b=Bag()
        for shared_id,so in sharedObjects.items():
            subscribers = []
            for page_id in so.subscribed_pages.keys():
                subscribers.append('%s[%s]' %(pages[page_id].user,page_id))
            b.setItem(shared_id,None,subscribed_pages='<br/>'.join(subscribers))
        return b


    def getUsers(self):
        result = Bag()
        users = self.asyncServer.users
        for user,userdict in users.items():
            connections = Bag()
            result.setItem(user, connections, start_ts=userdict['start_ts'],user=user)
            for connection_id,connectiondict in userdict['connections'].items():
                pages = Bag()
                connections.setItem(connection_id, pages, connection_id=connection_id,
                                    user_ip=connectiondict['user_ip'],
                                    start_ts=connectiondict['start_ts'])
                for page_id,page in connectiondict['pages'].items():
                    kw = dict([(key,getattr(page,key,None)) for key in ('page_id','connection_id','user')])
                    pages.setItem(page_id,None,**kw)
        return result




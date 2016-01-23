# -*- coding: UTF-8 -*-
from gnr.core.gnrdecorator import websocket_method
from gnr.core.gnrbag import Bag

class GnrCustomWebPage(object):
    py_requires = 'public:Public'
    def main(self,root,**kwargs):
        bc = root.borderContainer(datapath='main')
        top = bc.contentPane(region='top', height='50px')
        top.dataRpc('.data', self.getInfo,httpMethod='WSK',_timing=.5)

        bc.roundedGroupFrame(title='Pages',region='left',width='50%').quickgrid(value='^.data.pages')
        bc.roundedGroupFrame(title='Shared Objects',region='center').quickgrid(value='^.data.sharedObjects')

        
        
        
    @websocket_method
    def getInfo(self,**kwargs):
        return Bag(dict(pages=self.getPages(),sharedObjects= self.getSharedObjects()))

    def getPages(self):
        pages= self.asyncServer.pages
        b=Bag()
        for page_id,page in pages.items():
            kw = dict([(key,getattr(page,key,None)) for key in ('page_id','connection_id','user')])
            b[page_id] = Bag(kw)
        return b


    def getSharedObjects(self):
        sharedObjects= self.asyncServer.sharedObjects
        b=Bag()
        for shared_id,so in sharedObjects.items():
            print 'so',so.subscribed_pages
            kw = dict(subscribed_pages=','.join(so.subscribed_pages.keys()))
            b[shared_id] = Bag(kw)
        return b


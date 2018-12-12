# -*- coding: utf-8 -*-
from gnr.core.gnrdecorator import websocket_method
from gnr.core.gnrbag import Bag

class GnrCustomWebPage(object):
    def main(self,root,**kwargs):
        bc = root.borderContainer(datapath='main')
        top = bc.contentPane(region='top', height='50px')
        fb = top.formBuilder(cols=4)
        fb.button(label='getPages',fire='.getPages')
        top.dataRpc('.pages', self.getPages, _fired='^.getPages',httpMethod='WSK',_timing=.5)

        bc.contentPane(region='center').quickgrid(value='^.pages')

        
        
        
    @websocket_method
    def getPages(self,**kwargs):
        pages= self.asyncServer.pages
        b=Bag()
        for k,page in pages.items():
            kw = dict([(key,getattr(page,key,None)) for key in ('page_id','connection_id','user')])
            print k,kw
            b[k] = Bag(kw)
        return b


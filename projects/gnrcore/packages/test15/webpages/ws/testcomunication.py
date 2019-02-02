# -*- coding: utf-8 -*-
from builtins import object
from gnr.core.gnrdecorator import websocket_method, public_method
from gnr.core.gnrbag import Bag
#import wdb
class GnrCustomWebPage(object):

    def main(self,root,**kwargs):
        bc = root.borderContainer(height='100%')
        top = bc.contentPane(region='top', height='150px', datapath='ws_top')
        
        top.dataRpc('.pages', self.getPages, _fired='^.getPages',httpMethod='WSK')
        fb = top.formBuilder(cols=4)
        fb.button(label='getPages',fire='.getPages')
        fb.quickgrid(value='^.pages',height='300px',width='400px')
        
        
    @websocket_method
    def getPages(self):
        #wdb.set_trace()
        pages= self.ws_site.pages
        b=Bag()
        for k,page in list(pages.items()):
            b[k]=Bag(dict(pageid=k))
        return b


    @public_method
    def test_rpc(self):
        return 'test ok'

# -*- coding: UTF-8 -*-
from gnr.core.gnrdecorator import websocket_method, public_method

class GnrCustomWebPage(object):
    
    def isDeveloper(self):
        return True

    def main(self,root,**kwargs):
        bc = root.borderContainer(datapath='main')
        bc.data('.shared',None,shared_id='pippo',shared_expire=-1)
        bc.contentPane(region='top',height='100px',background='red')
        bc.contentPane(region='center')


# -*- coding: utf-8 -*-
from gnr.core.gnrdecorator import websocket_method, public_method
from gnr.core.gnrbag import Bag
class GnrCustomWebPage(object):
    
    def isDeveloper(self):
        return True

    def main(self,root,room=None,**kwargs):
        bc = root.borderContainer(datapath='main')
       #
       #room = room or 'collaborative_test'
       #bc.data('.shared',None,shared_id=room,shared_expire=10,shared_autoSave=True,shared_autoLoad=True)
       ##bc.sharedData('.shared',shared_id='collaborative_test',shared_expire=10000)
        top = bc.contentPane(region='top')
        top.data('ob',Bag(dict(top='100px',left='100px')))
        fb = top.div(padding='10px').formbuilder(cols=2,border_spacing='3px',datapath='.shared.info')
        fb.button('make',action='')
        center=bc.contentPane(region='center')

        m=center.div(position='absolute',border='1px solid red',
                         top='^ob.top',width='100px',height='100px',left='^ob.left',
                             background='yellow',moveable=True)
        m.div('^ob.top')
        m.div('^ob.left')

        
        
        


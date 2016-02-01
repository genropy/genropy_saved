# -*- coding: UTF-8 -*-
from gnr.core.gnrdecorator import websocket_method, public_method

class GnrCustomWebPage(object):
    
    def isDeveloper(self):
        return True

    def main(self,root,room=None,**kwargs):
        bc = root.borderContainer(datapath='main')
        room = room or 'collaborative_test'
        bc.data('.shared',None,shared_id=room,shared_expire=10,shared_autoSave=True,shared_autoLoad=True)
        #bc.sharedData('.shared',shared_id='collaborative_test',shared_expire=10000)
        top = bc.contentPane(region='top')
        fb = top.div(padding='10px').formbuilder(cols=2,border_spacing='3px',datapath='.shared.info')
        fb.textbox(value='^.alfa',lbl='Alfa')
        fb.textbox(value='^.beta',lbl='Beta')
        fb.textbox(value='^.gamma',lbl='Gamma')
        fb.textbox(value='^.delta',lbl='Delta')
        fb.button('Save',action='genro.wsk.saveSharedObject(room);',room=room)

        fb.button('Load',action='genro.wsk.loadSharedObject(room);',room=room)

        #fb.button('Subscribe',action="""
        #    genro.som.registerSharedObject('main.shared','collaborative_test',{expire:20})""")
#
        fb.button('Unregister',action="""
            genro.som.unregisterSharedObject(room);
        """,room=room)
#
        #bc.contentPane(region='center')


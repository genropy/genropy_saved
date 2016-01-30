# -*- coding: UTF-8 -*-
from gnr.core.gnrdecorator import websocket_method, public_method

class GnrCustomWebPage(object):
    
    def isDeveloper(self):
        return True

    def main(self,root,**kwargs):
        bc = root.borderContainer(datapath='main')
        #bc.data('.shared',None,shared_id='collaborative_test',shared_expire=10000)
        #bc.sharedData('.shared',shared_id='collaborative_test',shared_expire=10000)
        top = bc.contentPane(region='top')
        fb = top.div(padding='10px').formbuilder(cols=2,border_spacing='3px',datapath='.shared.info')
        fb.textbox(value='^.alfa',lbl='Alfa')
        fb.textbox(value='^.beta',lbl='Beta')
        fb.textbox(value='^.gamma',lbl='Gamma')
        fb.textbox(value='^.delta',lbl='Delta')

        fb.button('Subscribe',action="""
            genro.wsk.registerSharedObject('main.shared','collaborative_test',{expire=20})""")

        fb.button('Unregister',action="""
            genro.wsk.unregisterSharedObject('collaborative_test');
        """)
#
        #bc.contentPane(region='center')


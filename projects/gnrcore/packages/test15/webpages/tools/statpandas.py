# -*- coding: utf-8 -*-

# sharedobjects.py
# Created by Francesco Porcari on 2012-01-03.
# Copyright (c) 2012 Softwell. All rights reserved.


from __future__ import print_function
from builtins import object
from gnr.core.gnrdecorator import websocket_method, public_method


"Test sharedobjects"
class GnrCustomWebPage(object):
    py_requires="""gnrcomponents/testhandler:TestHandlerFull,
                  js_plugins/statspane/statspane:PdCommandsGrid"""
    dojo_source = True

    def windowTitle(self):
        return 'Stat pandas'

    def test_1_pandasSharedObject(self,pane):
        pane.pdCommandsGrid('test_1',height='300px',width='800px')

        
    def test_2_ripasso_ws(self,pane,**kwargs):
        fb = pane.formBuilder(cols=2)
        #### WEBSOCKET
        fb.button(label='WebSocket', action="""FIRE .websocket_test """)
        fb.dataRpc('.ws_result', self.test_ws, _fired='^.websocket_test',httpMethod='WSK')
        fb.div('^.ws_result')


        #### RPC
        fb.button(label='RPC', action="""FIRE .rpc_test_bt """)
        fb.dataRpc('.rpc_result', self.test_rpc, _fired='^.rpc_test_bt')
        fb.div('^.rpc_result')

    @websocket_method
    def test_ws(self,**kwargs):
        print('test_ws')
        return self.language or 'No'


    @public_method
    def test_rpc(self,**kwargs):
        return self.locale


    


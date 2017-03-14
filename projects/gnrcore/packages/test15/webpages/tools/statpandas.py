# -*- coding: UTF-8 -*-

# sharedobjects.py
# Created by Francesco Porcari on 2012-01-03.
# Copyright (c) 2012 Softwell. All rights reserved.


from gnr.core.gnrdecorator import websocket_method, public_method
from time import sleep
import thread

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
        fb = pane.formBuilder(cols=4)
        #### WEBSOCKET
        fb.button(label='WebSocket', action="""FIRE websocket_test_bt """)
        fb.dataController("""SET result.time=new Date();
            ; FIRE websocket_test """,_fired='^websocket_test_bt', __timing=1)
        fb.div('^result.websocket_result')
        fb.div('^result.diff_ws')
        fb.dataRpc('result.websocket_result', self.test_ws, _fired='^websocket_test',httpMethod='WSK')
        fb.dataController(""" var now = new Date();
                SET result.diff_ws = now-last_set;""", last_set = '=result.time',_fired='^result.websocket_result')
        

        #### RPC
        fb.button(label='RPC', action="""FIRE rpc_test_bt """)
        fb.dataController("""SET result.time=new Date();
            ; FIRE rpc_test """,_fired='^rpc_test_bt', __timing=1)
        fb.dataRpc('result.rpc_result', self.test_rpc, _fired='^rpc_test')
        fb.div('^result.rpc_result')
        fb.div('^result.diff_rpc')
        fb.dataController(""" var now = new Date();
                SET result.diff_rpc = now-last_set;""", last_set = '=result.time',_fired='^result.rpc_result')
        
    @websocket_method
    def test_ws(self,**kwargs):
        th_id = thread.get_ident()
        print 'received websocket call',th_id
        with self.sharedData('df') as dataframes:
            print 'lock acquired df'
            if 'pippo' not in dataframes:
                dataframes['pippo'] = 0
            else:
                dataframes['pippo']+=1
            sleep(2)
        print 'relased lock'
        print 'after 1 dataframes[pippo]',dataframes['pippo']
        return 'test ok'


    @public_method
    def test_rpc(self,**kwargs):
        print 'received http call',kwargs
        return 'test ok'

    


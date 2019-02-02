# -*- coding: utf-8 -*-
from builtins import object
from gnr.core.gnrdecorator import websocket_method, public_method

class GnrCustomWebPage(object):
    dojo_source=True
    py_requires='th/th:TableHandler'
    def isDeveloper(self):
        return True

    def main(self,root,**kwargs):
        bc = root.borderContainer(datapath='mainpane')
        top = bc.contentPane(region='top', height='200px')
        fb = top.formBuilder(cols=2)
        fb.dbSelect(value='^.user_rpc',dbtable='adm.user',lbl='User RPC')
        fb.dbSelect(value='^.user_wsk',
                    dbtable='adm.user',lbl='User WSK',
                    httpMethod='WSK'
                   )
        #### WEBSOCKET
        fb.button(label='WebSocket', action="""FIRE websocket_test_bt """)
        fb.dataController("""SET result.time=new Date();
            ; FIRE websocket_test """,_fired='^websocket_test_bt')#, _timing=1)
        fb.div('^result.websocket_result')
        fb.div('^result.diff_ws')
        fb.dataRpc('result.websocket_result', self.test_ws, _fired='^websocket_test',httpMethod='WSK')
        fb.dataController(""" var now = new Date();
                SET result.diff_ws = now-last_set;""", last_set = '=result.time',_fired='^result.websocket_result')
        
        
        #### RPC
        fb.button(label='RPC', action="""FIRE rpc_test_bt """)
        #fb.dataController("""console.log('scatto')
            #SET result.time=new Date(); FIRE rpc_test;""",_fired='^rpc_test_bt', _timing=1)

        fb.dataRpc('result.rpc_result', self.test_rpc, _fired='^rpc_test')
        fb.div('^result.rpc_result',lbl='Rpc result')
        fb.div('^result.diff_rpc',lbl='Diff rpc')
        fb.dataController(""" var now = new Date();
                SET result.diff_rpc = now-last_set;""", last_set = '=result.time',_fired='^result.rpc_result')
        center = bc.contentPane(region='center',border_top='1px solid blue',datapath='.datarpc')
        center.plainTableHandler(table='fatt.fattura',virtualStore=True,extendedQuery=True)
      
    @websocket_method
    def test_ws(self):
        return 'test ok'


    @public_method
    def test_rpc(self):
        return 'test ok'

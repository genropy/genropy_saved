# -*- coding: UTF-8 -*-

# public_monitor.py
# Created by Francesco Porcari on 2010-09-30.
# Copyright (c) 2010 Softwell. All rights reserved.


from gnr.web.gnrwebpage import BaseComponent

class PublicBatchMonitor(BaseComponent):
    py_requires = 'gnrcomponents/batch_handler/batch_handler:BatchMonitor'
    def pbl_left_batchmonitor(self,pane,footer=None,toolbar=None):
        "Batch Monitor"
        footer.button('!!Batch',showLabel=False,
                     action='PUBLISH bm_monitor_open;',
                     iconClass='icnBaseAction',float='right')
        toolbar.div('Batch',float='left')
        
        pane.dataController("SET pbl.left_stack = 'batchmonitor';",subscribe_bm_monitor_open=True)
        pane.dataController("""
                            if(pbl_left_stack_selected[0]=='batchmonitor_hide'){
                                PUBLISH bm_monitor_close;
                            };
                            """,subscribe_pbl_left_stack_selected=True,subscribe_pbl_mainMenuStatus=True,
                            _if='_reason=="pbl_left_stack_selected"',
                            _else="""
                                    if(currentStack=='batchmonitor'){
                                        if (pbl_mainMenuStatus[0]==false){
                                            PUBLISH bm_monitor_close;
                                        }else{
                                            PUBLISH bm_monitor_open;
                                        }
                                    }""",currentStack='=pbl.left_stack')
        self.bm_monitor_pane(pane)
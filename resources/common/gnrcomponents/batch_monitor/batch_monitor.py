# -*- coding: UTF-8 -*-

# chat_component.py
# Created by Francesco Porcari on 2010-09-08.
# Copyright (c) 2010 Softwell. All rights reserved.

from gnr.web.gnrwebpage import BaseComponent
from gnr.core.gnrbag import Bag
from datetime import datetime

class BatchMonitor(BaseComponent):
    js_requires = 'gnrcomponents/batch_monitor/batch_monitor'
    css_requires = 'gnrcomponents/batch_monitor/batch_monitor'
    def pbl_left_batchmonitor(self,pane,footer=None,toolbar=None):
        "Batch Monitor"
        footer.button('!!Batch',showLabel=False,
                     action='SET pbl.left_stack = "batchmonitor";',
                     iconClass='icnBaseAction',float='right')
        toolbar.div('Batch',float='left')
        pane.dataRpc('dummy','setStoreSubscription',subscribe='==_selected_stack=="batchmonitor"',
                    _selected_stack='^pbl.left_stack',storename='user',
                    client_path='gnr.batch')        
        pane.dataController("if(selected_stack=='batchmonitor'){genro.rpc.setPolling(1,1)}else{genro.rpc.setPolling();}",selected_stack='^pbl.left_stack')
        self.bm_monitor_pane(pane)
        
    def bm_monitor_pane(self,pane):
        pane.dataController("""var callname = 'on_'+_triggerpars.kw.reason;
                            if(callname in batch_monitor){
                                batch_monitor[callname].call(batch_monitor,_node);
                            }""",_fired="^gnr.batch")
        pane.div(nodeId='bm_rootnode',_class='bm_rootnode',overflow='auto',height='100%')
        
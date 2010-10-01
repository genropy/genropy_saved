# -*- coding: UTF-8 -*-

# chat_component.py
# Created by Francesco Porcari on 2010-09-08.
# Copyright (c) 2010 Softwell. All rights reserved.

from gnr.web.gnrwebpage import BaseComponent

class BatchMonitor(BaseComponent):
    js_requires = 'gnrcomponents/batch_monitor/batch_monitor'
    css_requires = 'gnrcomponents/batch_monitor/batch_monitor'
        
    def bm_monitor_pane(self,pane):
        pane.dataController("batch_monitor.on_datachange(_triggerpars.kw);",_fired="^gnr.batch")
        pane.div(nodeId='bm_rootnode',_class='bm_rootnode',overflow='auto',height='100%')
        pane.dataRpc('dummy','setStoreSubscription',subscribe_bm_monitor_open=True,
                    storename='user',client_path='gnr.batch',active=True,
                    _onResult='genro.rpc.setPolling(1,1);')
        pane.dataRpc('dummy','setStoreSubscription',active=False,subscribe_bm_monitor_close=True,
                    _onResult='genro.rpc.setPolling();')
        
# -*- coding: UTF-8 -*-

# thermo.py
# Created by Francesco Porcari on 2010-09-03.
# Copyright (c) 2010 Softwell. All rights reserved.
# 
# 
import os
from gnr.core.gnrbag import Bag
import time

class GnrCustomWebPage(object):
    dojo_version='11'
    py_requires="gnrcomponents/testhandler:TestHandlerFull,gnrcomponents/thermopane:ThermoPane"

    def windowTitle(self):
        return 'Thermo'
         
    def test_1_thermo(self,pane):
        """Thermo"""
        bc = pane.borderContainer(height='400px',datapath='test1') 
        bc.data('_thermo.auto_polling',3)
        bc.data('_thermo.user_polling',.5)

        bc.data('_thermo.data',None,_serverpath='_thermo')
        top = bc.contentPane(region='left')
        top.button('Start',fire='.start_test')        
        center = bc.contentPane(region='center') 
        center.button('Open floating',action='genro.dlg.batchMonitor();')
        center.dataController("""
                                 FIRE .run_rpc;""",_fired="^.start_test")
        center.dataRpc('dummy','test_thermo',_fired='^.run_rpc',thermo_id='mythermo',thermo_item='clients')
                    
        top.dataController("""genro.rpc.setPolling(auto_polling&&monitor,user_polling&&monitor);""",
                           monitor='^_thermo.monitor',auto_polling='=_thermo.auto_polling',
                           user_polling='=_thermo.user_polling')
        
    def thermo_test(self):
        result = Bag()
        th=Bag()
        th.setItem('lines.clients',None,progress=0,maximum=50,message='Rufus Baboden')
        th.setItem('lines.invoices',None,progress=13,maximum=20,message='IN:10.1209 - 23/07/2010')
        result.setItem('print_inv',th,thermotitle='Invoice printing')
        th=Bag()
        th.setItem('lines.jobs',None,progress=300,maximum=1000,message='BK208089-client:Landers')
        result.setItem('print_jobs',th,thermotitle='Job batch print')
        return result
    
    def rpc_test_thermo(self,thermo_id,thermo_item=None):
        request=self.request._request
        t = time.time()
        maximum=20
        self.start_thermo(thermo_id,thermo_item,maximum=maximum,message='Starting...')
        for k in range(maximum+1):
            time.sleep(1)
            self.update_thermo(thermo_id,thermo_item,progress=k,maximum=maximum,message='working %i' %k)
        time.sleep(1)
        result = Bag()
        result['esito'] = 'done'
        result['tempo'] =str(time.time()-t)
        self.end_thermo(thermo_id)
        return result

    def start_thermo(self,thermo_id,thermo_item,maximum=None,message=None):
        with self.pageStore() as store:
            store.setItem('_thermo.%s.lines.%s' %(thermo_id,thermo_item),0,
                            message=message,maximum=maximum)
        
    def update_thermo(self,thermo_id,thermo_item,progress=None,message=None,maximum=None):
        with self.pageStore() as store:
            store.setItem('_thermo.%s.lines.%s' %(thermo_id,thermo_item),progress,
                            progress=progress,message=message,maximum=maximum)
                            
    def end_thermo(self,thermo_id):
        with self.pageStore() as store:
            store.setItem('_thermo.%s.status.end' %thermo_id,True)
    
    def doc_thermo(self):
        """
         _thermo.data
            .mythermo
                    .lines
                        .client
                        .invoice
                        .rows
                     .status
                         .end
            .yourthermo
                    .foo
        .show
 
        """
        pass

# -*- coding: UTF-8 -*-

# thermo.py
# Created by Francesco Porcari on 2010-09-03.
# Copyright (c) 2010 Softwell. All rights reserved.
# 
# 
import os
from gnr.core.gnrbag import Bag
import random
import time

class GnrCustomWebPage(object):
    dojo_version='11'
    py_requires="gnrcomponents/testhandler:TestHandlerFull,gnrcomponents/thermopane:ThermoPane"

    def windowTitle(self):
        return 'Thermo'
         
    def test_1_batch(self,pane):
        "Batch"
        box = pane.div(datapath='test1')
        box.button('Start',fire='.start_test')      
        box.dataRpc('dummy','test_1_batch',_fired='^.start_test')
    
    def rpc_test_1_batch(self,):
        t = time.time()
        cli_max = 10
        invoice_max = 10
        row_max = 50
        sleep_time = 0.05

        thermo_lines='clients,invoices,rows'
       # thermo_lines = [{'title':'Clients',_class=}]
        self.btc.batch_create(title='testbatch',
                              thermo_lines=thermo_lines,note='This is a test batch %i' %int(random.random()*100))
        clients = int(random.random() *cli_max)
        #self.btc.thermo_line_start(line='clients',maximum=clients)
        try:
            for client in range(1,clients+1):
                stopped = self.btc.thermo_line_update(line='clients',
                                            maximum=clients,message='client %i/%i' %(client,clients),progress=client)
                
                invoices = int(random.random() *invoice_max)
                #self.btc.thermo_line_start(line='invoices',maximum=invoices)
            
                for invoice in range(1,invoices+1):
                    stopped= self.btc.thermo_line_update(line='invoices',
                                                maximum=invoices,message='invoice %i/%i' %(invoice,invoices),progress=invoice)
                    rows = int(random.random() *row_max)
                    #self.btc.thermo_line_start(line='rows',maximum=rows)
                
                    for row in range(1,rows+1):
                        stopped = self.btc.thermo_line_update(line='rows',
                                                    maximum=rows,message='row %i/%i' %(row,rows),progress=row)
                        time.sleep(sleep_time)
        except self.btc.exception_stopped:
            self.btc.batch_aborted()
       #except Exception, e:
       #    self.btc.batch_error(error=str(e))
        self.btc.batch_complete(result='Execution completed',result_attr=dict(url='http://www.apple.com'))
        
          




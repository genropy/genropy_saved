# -*- coding: UTF-8 -*-

# thermo.py
# Created by Francesco Porcari on 2010-09-03.
# Copyright (c) 2010 Softwell. All rights reserved.

"""thermo"""

import random
import time

cli_max = 12
invoice_max = 20
row_max = 100
sleep_time = 0.05

class GnrCustomWebPage(object):
    dojo_version = '11'
    py_requires = "gnrcomponents/testhandler:TestHandlerFull,gnrcomponents/thermopane:ThermoPane"
    
    def windowTitle(self):
        return 'Thermo'
        
    def test_1_batch(self, pane):
        "Batch"
        box = pane.div(datapath='test1')
        box.button('Start', fire='.start_test')
        box.dataRpc('dummy', 'test_1_batch', _fired='^.start_test')
        
    def test_2_batch(self, pane):
        "Batch 2"
        box = pane.div(datapath='test2')
        box.button('Start', fire='.start_test')
        box.dataRpc('dummy', 'test_2_batch', _fired='^.start_test')
        
    def test_3_batch(self, pane):
        "Batch 3"
        box = pane.div(datapath='test3')
        box.button('Start', fire='.start_test')
        box.dataRpc('dummy', 'test_3_batch', _fired='^.start_test')
        
    def rpc_test_1_batch(self):
        t = time.time()
        # thermo_lines = [{'title':'Clients',_class=}]
        thermo_lines = 'clients,invoices,rows'
        thermo_lines = None
        self.btc.batch_create(title='testbatch',
                              thermo_lines=thermo_lines, note='This is a test batch_1 %i' % int(random.random() * 100))
        clients = int(random.random() * cli_max)
        self.btc.thermo_line_add(code='clients', maximum=clients)
        try:
            for client in range(1, clients + 1):
                stopped = self.btc.thermo_line_update(code='clients',
                                                      maximum=clients, message='client %i/%i' % (client, clients),
                                                      progress=client)
                                                      
                invoices = int(random.random() * invoice_max)
                self.btc.thermo_line_add(code='invoices', maximum=invoices)
                
                for invoice in range(1, invoices + 1):
                    stopped = self.btc.thermo_line_update(code='invoices',
                                                          maximum=invoices,
                                                          message='invoice %i/%i' % (invoice, invoices),
                                                          progress=invoice)
                    rows = int(random.random() * row_max)
                    self.btc.thermo_line_add(code='rows', maximum=rows)
                    for row in range(1, rows + 1):
                        stopped = self.btc.thermo_line_update(code='rows',
                                                              maximum=rows, message='row %i/%i' % (row, rows),
                                                              progress=row)
                        time.sleep(sleep_time)
                    self.btc.thermo_line_del(code='rows')
                self.btc.thermo_line_del(code='invoices')
            self.btc.thermo_line_del(code='clients')
            
        except self.btc.exception_stopped:
            self.btc.batch_aborted()
        except Exception, e:
            self.btc.batch_error(error=str(e))
        self.btc.batch_complete(result='Execution completed', result_attr=dict(url='http://www.apple.com'))
        
    def rpc_test_2_batch(self):
        t = time.time()
        thermo_lines = 'clients,invoices,rows'
        thermo_lines = None
        self.btc.batch_create(title='testbatch',
                              thermo_lines=thermo_lines, note='This is a test batch_2 %i' % int(random.random() * 100))
        try:
            clients = int(random.random() * cli_max)
            for client in self.client_provider(clients):
                invoices = int(random.random() * invoice_max)
                for invoice in self.invoice_provider(invoices):
                    rows = int(random.random() * row_max)
                    for row in self.row_provider(rows):
                        time.sleep(sleep_time)
        except self.btc.exception_stopped:
            self.btc.batch_aborted()
        except Exception, e:
            self.btc.batch_error(error=str(e))
        self.btc.batch_complete(result='Execution completed', result_attr=dict(url='http://www.apple.com'))
        
    def client_provider(self, clients):
        self.btc.thermo_line_add(code='clients', maximum=clients)
        for client in range(1, clients + 1):
            self.btc.thermo_line_update(code='clients',
                                        maximum=clients, message='client %i/%i' % (client, clients), progress=client)
            yield client
        self.btc.thermo_line_del(code='invoices')
        
    def invoice_provider(self, invoices):
        self.btc.thermo_line_add(code='invoices', maximum=invoices)
        for invoice in range(1, invoices + 1):
            self.btc.thermo_line_update(code='invoices',
                                        maximum=invoices, message='invoice %i/%i' % (invoice, invoices),
                                        progress=invoice)
            yield invoice
        self.btc.thermo_line_del(code='invoices')
        
    def row_provider(self, rows):
        self.btc.thermo_line_add(code='rows', maximum=rows)
        for row in range(1, rows + 1):
            self.btc.thermo_line_update(code='rows',
                                        maximum=rows, message='row %i/%i' % (row, rows), progress=row)
            yield row
        self.btc.thermo_line_del(code='rows')
        
    def rpc_test_3_batch(self):
        t = time.time()
        btc = self.btc
        self.btc.batch_create(title='testbatch', note='This is a test batch_3 %i' % int(random.random() * 100))
        
        def clients_cb():
            return range(int(random.random() * cli_max))
            
        def invoices_cb(client=None):
            return range(int(random.random() * invoice_max))
            
        def rows_cb(invoice=None):
            return range(int(random.random() * row_max))
            
        try:
            for client in btc.thermo_wrapper(clients_cb, 'clients'):
                for invoice in btc.thermo_wrapper(invoices_cb, 'invoices', client=client):
                    for row in btc.thermo_wrapper(rows_cb, 'rows', invoice=invoice):
                        time.sleep(sleep_time)
        except self.btc.exception_stopped:
            self.btc.batch_aborted()
        except Exception, e:
            self.btc.batch_error(error=str(e))
        self.btc.batch_complete(result='Execution completed', result_attr=dict(url='http://www.apple.com'))
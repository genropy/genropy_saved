#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  untitled
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#
from gnr.web.gnrwebpage_proxy.gnrbaseproxy import GnrBaseProxy
from gnr.core.gnrbag import Bag
from datetime import datetime             
from gnr.core.gnrlang import timer_call,debug_call

class GnrBatchStoppedException(Exception):
     pass
             

class GnrWebBatch(GnrBaseProxy):
    exception_stopped = GnrBatchStoppedException
    
    def init(self, connection_id=None,user=None,**kwargs):
        pass
        
    
    @property
    def batch_path(self):
        return 'gnr.batch.%s' %self.batch_id
    
    @property
    def result_doc_path(self):
        return self.page.userDocument('_batch_result','b_%s.xml' %self.batch_id)
        
    #@debug_call
    def batch_create(self,batch_id=None,title=None,thermo_lines=None,note=None,cancellable=True,delay=1):
        self.batch_id = batch_id or self.page.getUuid()
        self.title = title
        self.thermo_lines = thermo_lines
        if isinstance(thermo_lines,basestring):
            self.last_line = thermo_lines.split(',')[-1]
        else:
            self.last_line = thermo_lines[-1]['code']
        self.note = note
        self.start_ts=datetime.now()
        self.last_ts = self.start_ts
        self.cancellable = True
        self.delay = delay
        
        with self.page.userStore() as store:
            store.drop_datachanges(self.batch_path)
            newbatch = Bag(dict(title=title,start_ts=self.start_ts,lines=thermo_lines,note=note,
                                thermo=Bag(dict([(k,None) for k in thermo_lines.split(',')],
                                cancellable = cancellable)
                           )))    
            store.set_datachange(self.batch_path,newbatch,reason='btc_create')
        return batch_id
        
    #@debug_call
    def batch_complete(self, result=None,result_attr=None):
        result_doc = self._result_write(result=result,result_attr=result_attr)
        with self.page.userStore() as store:
            store.set_datachange('%s.end' %self.batch_path,True,reason='btc_end')
            store.set_datachange(self.batch_path,result_doc,reason='btc_result_doc')
    
    def batch_error(self, error=None,error_attr=None):
        error_doc = self._result_write(error=error,error_attr=error_attr)
        with self.page.userStore() as store:
            store.set_datachange('%s.error' %self.batch_path,True,reason='btc_error')
            store.set_datachange(self.batch_path,error_doc,reason='btc_error_doc')
    
    def batch_aborted(self):
        with self.page.userStore() as store:
            store.drop_datachanges(self.batch_path)
            store.set_datachange(self.batch_path,delete=True,reason='btc_aborted')
            
    def rpc_abort_batch(self,batch_id):
        self.batch_id = batch_id
        with self.page.userStore() as store:
            store.setItem('%s.stopped' %self.batch_path,True)
        
        
        
    def _result_write(self,result=None,result_attr=None,error=None,error_attr=None):
        result_doc = Bag()
        result_doc['title'] = self.title
        result_doc['note'] = self.note
        result_doc['start_ts'] = self.start_ts
        result_doc['end_ts'] = datetime.now()
        result_doc['time_delta'] = str(result_doc['end_ts']-result_doc['start_ts']).split('.')[0]
        if result is not None:
            result_doc.setItem('result',result,_attributes=result_attr)
        if error is not None:
            result_doc.setItem('error',error,_attributes=error_attr)
        result_doc.toXml(self.result_doc_path,autocreate=True)
        return result_doc
    
    def result_load(self,batch_id):
        self.batch_id = batch_id
        result_doc = Bag(self.result_doc_path)
        return result_doc
                
    def thermo_cleanup(self,thermo_lines=None):
        with self.page.userStore() as store:
            for line in thermo_lines.split(','):
                store.set_datachange('%s.thermo.%s' %(self.batch_path,line),Bag(),reason='th_cleanup')

    #@debug_call
    def thermo_line_start(self,line,maximum=None,message=None):
        with self.page.userStore() as store:
            store.set_datachange('%s.thermo.%s' %(self.batch_path,line),0,
                            attributes=dict(message=message,maximum=maximum),reason='tl_start')
        
    #@debug_call
    def thermo_line_update(self,line,progress=None,message=None,maximum=None):
        curr_time = datetime.now()
        if line==self.last_line and ((datetime.now()-self.last_ts).seconds<self.delay):
            return
        print message
        self.last_ts = curr_time
        with self.page.userStore() as store:
            if self.cancellable and store.getItem('%s.stopped' %self.batch_path):
                raise GnrBatchStoppedException('Execution stopped by user')
            store.set_datachange('%s.thermo.%s' %(self.batch_path,line),progress,
                            attributes=dict(progress=progress,message=message,maximum=maximum),replace=True,
                            reason='tl_upd')
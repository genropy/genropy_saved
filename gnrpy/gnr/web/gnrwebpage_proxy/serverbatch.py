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
import os  
from gnr.core.gnrlang import timer_call,debug_call

class GnrBatchStoppedException(Exception):
     pass
             

class GnrWebBatch(GnrBaseProxy):
    exception_stopped = GnrBatchStoppedException
    
    def init(self, connection_id=None,user=None,**kwargs):
        pass
        
    def on_authenticated(self,user):
        if not os.path.exists(self.page.userDocument('_batch_result')):
            return
        batch_results = os.listdir(self.page.userDocument('_batch_result'))
        with self.page.userStore(user) as store:
            already_registered_batch = [dc.path.split('.')[2] for dc in store.datachanges if dc.path.startswith('gnr.batch')]
            for res_doc_name in batch_results:
                result_doc = Bag(self.page.userDocument('_batch_result',res_doc_name))
                batch_id = result_doc['batch_id']
                if batch_id not in already_registered_batch:
                    batch_path = 'gnr.batch.%s' %batch_id
                    newbatch = Bag(dict(title=result_doc['title'],start_ts=result_doc['start_ts'],note=result_doc['note'],
                                        owner_page_id=result_doc['owner_page_id']))    
                    store.set_datachange(batch_path,newbatch,reason='btc_create')
                    reason = 'btc_result_doc' if result_doc['result'] else 'btc_error_doc'
                    store.set_datachange(batch_path,result_doc,reason=reason)


    @property
    def batch_path(self):
        return 'gnr.batch.%s' %self.batch_id
    
    @property
    def result_doc_path(self):
        return self.page.userDocument('_batch_result','b_%s.xml' %self.batch_id)
        
        
    def run_batch(self,gnrbatch):
        self.batch_create(batch_id='%s_%s' %(gnrbatch.batch_prefix,self.page.getUuid()),
                            title=gnrbatch.batch_title,thermo_lines=gnrbatch.batch_thermo_lines,
                            cancellable=gnrbatch.batch_cancellable,delay=gnrbatch.batch_delay,note=gnrbatch.batch_note)
        #try:
        if True:
            batch_result = gnrbatch.run()
        #except self.exception_stopped:
        else:
            self.batch_aborted()
        url = None
        result = 'Execution completed'
        result_attr = dict()
        if isinstance(batch_result,basestring):
            url = batch_result
        else:
            url = batch_result['url']
            result = batch_result['result']
            result_attr = batch_result['attr'] 
        if url:
            result_attr['url'] = url
            
       #except Exception, e:
       #    self.btc.batch_error(error=str(e))
       
        self.batch_complete(result=result,result_attr=result_attr)
        
        
    #@debug_call
    def batch_create(self,batch_id=None,title=None,thermo_lines=None,note=None,cancellable=True,delay=1):
        self.batch_id = batch_id or self.page.getUuid()
        self.title = title
        self.line_codes = []
        if thermo_lines:
            if isinstance(thermo_lines,basestring):
                self.line_codes =  thermo_lines.split(',')
            else:
                self.line_codes = [line['code'] for line in thermo_lines]
        self.thermo_lines = thermo_lines
        
        self.note = note
        self.start_ts=datetime.now()
        self.last_ts = self.start_ts
        self.cancellable = True
        self.delay = delay
        
        with self.page.userStore() as store:
            store.drop_datachanges(self.batch_path)
            newbatch = Bag(dict(title=title,start_ts=self.start_ts,lines=thermo_lines,note=note,
                                owner_page_id=self.page.page_id,
                                thermo=Bag(dict([(k,None) for k in self.line_codes],cancellable = cancellable))))    
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
            store.set_datachange(self.batch_path,None,reason='btc_aborted')
    
    def rpc_remove_batch(self,batch_id):
        self.batch_id = batch_id
        with self.page.userStore() as store:
            store.drop_datachanges(self.batch_path)
            store.set_datachange(self.batch_path,None,reason='btc_removed')
        self._result_remove()
                    
    def rpc_abort_batch(self,batch_id):
        self.batch_id = batch_id
        with self.page.userStore() as store:
            store.setItem('%s.stopped' %self.batch_path,True)
        
        
    def _result_remove(self):
        os.remove(self.result_doc_path)    
    
    def _result_write(self,result=None,result_attr=None,error=None,error_attr=None):
        result_doc = Bag()
        result_doc['title'] = self.title
        result_doc['batch_id'] = self.batch_id
        result_doc['owner_page_id'] = self.page.page_id
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
    def thermo_line_add(self,code,maximum=None,message=None,thermo_class=None): 
        self.line_codes.append(code)           
        thermo_class = thermo_class or 'bm_line_%s' %len(self.line_codes)
        with self.page.userStore() as store:
            store.set_datachange('%s.thermo.%s' %(self.batch_path,code),0,
                            attributes=dict(message=message,maximum=maximum,batch_id=self.batch_id,thermo_class=thermo_class),reason='tl_add')
        
    def thermo_line_del(self,code):
        self.line_codes.remove(code)           
        with self.page.userStore() as store:
            store.set_datachange('%s.thermo.%s' %(self.batch_path,code),None,
                            attributes=dict(batch_id=self.batch_id),reason='tl_del')

    
    # #@debug_call
    def thermo_line_update(self,code,progress=None,message=None,maximum=None):
        if not code in self.line_codes:
            return
        curr_time = datetime.now()
        if progress>1 and code==self.line_codes[-1] and ((datetime.now()-self.last_ts).seconds<self.delay):
            return
        self.last_ts = curr_time
        with self.page.userStore() as store:
            if self.cancellable and store.getItem('%s.stopped' %self.batch_path):
                raise GnrBatchStoppedException('Execution stopped by user')
            store.set_datachange('%s.thermo.%s' %(self.batch_path,code),progress,
                            attributes=dict(progress=progress,message=message,maximum=maximum),replace=True,
                            reason='tl_upd')

    def thermo_wrapper(self,iterable,line_code,message=None,keep=True,**kwargs):
        """
        this method will return an iterator that wraps
        the give iterable and update the related thermo
        
        Params:
        * `iterable`:  it can be an iterable or a callable. If callable: it's called before iteration.
        * `line_code`: the code for the thermoline: if it's not existing it's created before iteration and removed at the end.
        * `message`:  it can be a callable: in this case it's called for any iteration with item, progress an maximum. If it's a string
                     it's used to create a standard message that adds progress/maximum. If it's omitted the line_code is used for message
        * `kwargs`: any given kwargs is passed to the iterable method
    
        """
        
        if isinstance(iterable,basestring):
            iterable = iterable.split(',')
        if callable(iterable):
            iterable=iterable(**kwargs)
        maximum=len(iterable)
        if callable(message):
            cb_message = message
        else:
            msg_desc = message or line_code
            cb_message = lambda item,k,m: '%s %i/%i'  %(msg_desc,k,m)
        if not line_code in self.line_codes:
            self.thermo_line_add(line_code,maximum=maximum)
        for k,item in enumerate(iterable):
            progress=k+1
            message = cb_message(item,progress,maximum,iterable=iterable)
            self.thermo_line_update(line_code,maximum=maximum,message=message,progress=progress)
            yield item
        if not keep:
            self.thermo_line_del(line_code)
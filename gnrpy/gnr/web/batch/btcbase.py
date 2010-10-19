#!/usr/bin/env python
# encoding: utf-8
"""
gnrserverbatch.py

Created by Francesco Porcari on 2010-10-16.
Copyright (c) 2010 Softwell. All rights reserved.
"""

from gnr.core.gnrbag import Bag

class BaseResourceBatch(object):
    batch_prefix = 'BB'
    batch_thermo_lines = 'batch_steps,batch_main,ts_loop'
    batch_title = 'My Batch Title'
    batch_cancellable = True
    batch_delay = 0.5
    batch_note = None
    batch_steps = None #'foo,bar'
    dialog_height = '200px'
    dialog_width = '300px'

    def __init__(self,page=None,resource_table=None):
        self.page = page
        self.db = self.page.db
        self.tblobj = resource_table
        self.maintable = resource_table.fullname
        self.btc = self.page.btc
        self.results = Bag()
        self._pkeys=None
    
    def x__call__(self,batch_note=None,**kwargs):
        parameters = kwargs['parameters']
        self.batch_parameters = parameters.asDict(True) if parameters else {}
        self.batch_note = batch_note
        try:
            self.run()
            self.btc.batch_complete(self.result_handler())
        except self.btc.exception_stopped:
            self.btc.batch_aborted()
        except Exception, e:
            if self.page.site.debug:
                raise e
            else:
                self.btc.batch_error(error=str(e))
                
    def __call__(self,batch_note=None,**kwargs):
        parameters = kwargs['parameters']
        self.batch_parameters = parameters.asDict(True) if parameters else {}
        self.batch_note = batch_note
        self.run()
        result,result_attr = self.result_handler()
        self.btc.batch_complete(result=result,result_attr=result_attr)
    
    def _pre_process(self):
        pass
        
    def run(self):
        self.btc.batch_create(batch_id='%s_%s' %(self.batch_prefix,self.page.getUuid()),
                            title=self.batch_title,
                            cancellable=self.batch_cancellable,delay=self.batch_delay,note=self.batch_note) 
        self._pre_process()
        if self.batch_steps:
            for step in self.btc.thermo_wrapper(self.batch_steps,'btc_steps',message=self.get_step_caption,keep=True):
                step_handler = getattr(self,'step_%s' %step)
                step_handler()
                for line_code in self.btc.line_codes[1:]:
                    self.btc.thermo_line_del(line_code)
        else:
            self.do()
    
    def storeResult(self,key,result):
        self.results[key] = result
    
    def batchUpdate(self, updater=None, table = None, where=None, line_code=None, message=None, **kwargs ):
        table = table or self.page.maintable
        tblobj = self.db.table(table)
        
        if not where:
            where='$%s IN:pkeys' % tblobj.pkey
            kwargs['pkeys'] = self.get_selection_pkeys()
            
        tblobj.batchUpdate(updater=updater, where=where,
                          _wrapper=self.btc.thermo_wrapper,
                            _wrapperKwargs=dict(line_code='date',
                                                message= message or self.get_record_caption,
                                                tblobj=tblobj), **kwargs)
        
    def result_handler(self):
        return 'Execution completed',dict()
        
    def get_step_caption(self,item,progress,maximum,**kwargs):
        step_handler = getattr(self,'step_%s' %item)
        return step_handler.__doc__
        
    def get_record_caption(self,item,progress,maximum, tblobj=None,**kwargs):
        if tblobj:
            caption = '%s (%i/%i)' % (tblobj.recordCaption(item),progress,maximum)
        else:
            caption = '%i/%i' % (progress,maximum)
        return caption

    def do(self,**kwargs):
        """override me"""
        pass
    
    def defineSelection(self,selectionName=None,selectedRowidx=None):
        self.selectionName = selectionName
        self.selectedRowidx = selectedRowidx
    
    def get_selection(self):
        selection = self.page.getUserSelection(selectionName=self.selectionName,
                                         selectedRowidx=self.selectedRowidx)
        return selection
    
    def get_records(self):
        pkeys = self.get_selection_pkeys()
        for pkey in pkeys:
            yield self.get_record(pkey)
    
    def get_record(self,pkey):
        return self.tblobj.record(pkey).output('bag')
        
    def get_selection_pkeys(self):
        if self._pkeys is None:
            self._pkeys = self.get_selection().output('pkeylist')
        return self._pkeys
        
    def rpc_selectionFilterCb(self,row):
        """override me"""
        return True
        
    def parameters_pane(self,pane,**kwargs):
        """Pass a ContentPane for adding forms to allow you to ask parameters to the clients"""
        pass
        
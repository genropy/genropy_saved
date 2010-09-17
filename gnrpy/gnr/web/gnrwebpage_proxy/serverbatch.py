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
        page=self.page
        self.user_agent=page.request.get_header('User-Agent') or ''
    
    def batch_running_path(self,batch_id):
        return 'gnr.batch.%s' %batch_id
        
    def batch_complete_path(self,batch_id):
        return 'gnr.batch.%s' %batch_id
        
        
    #@debug_call
    def batch_create(self,batch_id=None,title=None,thermo_lines=None,note=None):
        batch_id = batch_id or self.page.getUuid()
        with self.page.userStore() as store:
            newbatch = Bag(dict(title=title,start_ts=datetime.now(),lines=thermo_lines,note=note,
                                thermo=Bag(dict([(k,None) for k in thermo_lines.split(',')])
                           )))    
            store.set_datachange(self.batch_running_path(batch_id),newbatch)
        return batch_id
    #@debug_call
    def batch_complete(self,batch_id, result=None):
        with self.page.userStore() as store:
            store.set_datachange('%s.end' %self.batch_running_path(batch_id),True)
            #store.set_datachange(self.batch_running_path(batch_id),delete=True)
            store.set_datachange(self.batch_complete_path(batch_id),Bag(result))
    
    def batch_aborted(self,batch_id, result=None):
        with self.page.userStore() as store:
            store.set_datachange(self.batch_running_path(batch_id),delete=True)
            
    def thermo_cleanup(self,batch_id,thermo_lines=None):
        with self.page.userStore() as store:
            for line in thermo_lines.split(','):
                store.set_datachange('%s.thermo.%s' %(self.batch_running_path(batch_id),line),Bag())

    #@debug_call
    def thermo_line_start(self,batch_id,line,maximum=None,message=None):
        with self.page.userStore() as store:
            store.set_datachange('%s.thermo.%s' %(self.batch_running_path(batch_id),line),0,
                            attributes=dict(message=message,maximum=maximum))
        
    #@debug_call
    def thermo_line_update(self,batch_id,line,progress=None,message=None,maximum=None):
        with self.page.userStore() as store:
            if store.getItem('%s.stopped' %self.batch_running_path(batch_id)):
                raise GnrBatchStoppedException('Execution stopped by user')
            store.set_datachange('%s.thermo.%s' %(self.batch_running_path(batch_id),line),progress,
                            attributes=dict(progress=progress,message=message,maximum=maximum),replace=True)
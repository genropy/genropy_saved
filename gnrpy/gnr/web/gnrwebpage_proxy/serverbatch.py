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

class GnrBatchStoppedException(Exception):
     pass
             

class GnrWebBatch(GnrBaseProxy):
    exception_stopped = GnrBatchStoppedException
    
    def init(self, connection_id=None,user=None,**kwargs):
        page=self.page
        self.user_agent=page.request.get_header('User-Agent') or ''
    
    def batch_running_path(self,batch_id):
        return '_batch.running.%s' %batch_id
        
        
    def batch_create(self,batch_id=None,title=None,thermo_lines=None):
        batch_id = batch_id or self.page.getUuid()
        with self.userStore() as store:
            store.setItem(self.batch_running_path(batch_id),
                            Bag(dict(title=title,start_ts=datetime.now()),
                                      lines=Bag(dict([(k,None) for k in thermo_lines.split(',')]))
                                      ))
        return batch_id
    
    def batch_complete(self,batch_id, result=None):
        with self.userStore() as store:
            store.delItem(self.batch_running_path(batch_id))
            store.setItem(self.batch_complete_path(batch_id),Bag(result))
    
    def batch_aborted(self,batch_id, result=None):
        with self.userStore() as store:
            store.delItem(self.batch_running_path(batch_id))
            
    def thermo_cleanup(self,batch_id):
        def cb(n):
            n.setValue(Bag())
            
        with self.userStore() as store:
            store.getItem('%s.thermo' %self.batch_running_path(batch_id)).forEach(cb)

            
    def thermo_line_start(self,batch_id,line,maximum=None,message=None):
        with self.userStore() as store:
            store.setItem('%s.thermo.%s' %(self.batch_running_path(batch_id),line),0,
                            message=message,maximum=maximum)
        
    def thermo_line_update(self,batch_id,line,progress=None,message=None,maximum=None):
        with self.userStore() as store:
            if store.getItem('%s.thermo.%s.stopped' %(self.batch_running_path(batch_id),line)):
                raise GnrBatchStoppedException('Execution stopped by user')
            store.setItem('%s.thermo.%s' %(self.batch_running_path(batch_id),line),progress,
                            progress=progress,message=message,maximum=maximum)
                
                            
    def thermo_end(self,batch_id):
        with self.pageStore() as store:
            store.setItem('_batch..%s.status.end' %batch_id,True)
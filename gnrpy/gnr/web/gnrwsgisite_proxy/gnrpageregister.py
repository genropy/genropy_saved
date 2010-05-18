#-*- coding: UTF-8 -*-
#--------------------------------------------------------------------------
# package           : GenroPy web - see LICENSE for details
# module gnrwebcore : core module for genropy web framework
# Copyright (c)     : 2004 - 2007 Softwell sas - Milano 
# Written by    : Giovanni Porcari, Michele Bertoldi
#                 Saverio Porcari, Francesco Porcari , Francesco Cavazzana
#--------------------------------------------------------------------------
#This library is free software; you can redistribute it and/or
#modify it under the terms of the GNU Lesser General Public
#License as published by the Free Software Foundation; either
#version 2.1 of the License, or (at your option) any later version.

#This library is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
#Lesser General Public License for more details.

#You should have received a copy of the GNU Lesser General Public
#License along with this library; if not, write to the Free Software
#Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA
# 


MAX_RETRY=10
RETRY_TIME=0.01
LOCK_TIME=2
MSG_DEFAULT_EXPIRY=10

class PageRegister(object):
    
    def __init__(self, site):
        self.site = site
        self.sd=self.site.shared_data
    
    def register(self,page):
        """Register page"""
        
        
    def unregister(self,page):
        """Unregister page"""
        
    def refresh(self,page):
        """Register page"""
        
    def pages(self):
        """Registered pages"""
        address ='PAGE_REGISTER-%s-%s'%(dest_type,address)
        result=[]
        with self.sd.locked(key=address,max_retry=MAX_RETRY,lock_time=LOCK_TIME,retry_time=RETRY_TIME):
            cnt=sd.get_multi(['R','W'],'%s_' % address)
            r_msg=cnt.get('R',0)
            w_msg=cnt.get('W',0)
            if w_msg>r_msg:
                messages=sd.get_multi([str(k+1) for k in range(r_msg,w_msg)],'%s_' % address)
                result=[messages[str(k+1)] for k in range(r_msg,w_msg) if str(k+1) in messages]
                sd.set('%s_R' % address,w_msg)
        return result
        
        
    def subscribe(self,topic,page):
        self.message_handler.subscribe(topic,event)
        
    def publish(self,topic,cb):
        self.message_handler.publish(topic,event,cb)
        
    def subscribe(self,topic,subscriber_page_id):
        sd=self.site.shared_data
        address ='SUB-%s'%(topic)
        message=self._buildMessageEnvelope(body=body, message_type=message_type, 
                                src_connection_id=src_connection_id, 
                                src_user=src_user, src_page_id=src_page_id, **kwargs)
        with sd.locked(key=address,max_retry=MAX_RETRY, lock_time=LOCK_TIME, retry_time=RETRY_TIME):
            counter_w='%s_W' % address
            k=sd.incr(counter_w)
            if k is None:
                k=1
                sd.set(counter_w,k)
            key='%s_%i' % (address,k) 
            sd.set(key,message,expiry)
    
        
        
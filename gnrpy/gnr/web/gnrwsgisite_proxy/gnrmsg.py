#!/usr/bin/env python
# encoding: utf-8
"""
Created by Softwell on 2008-07-10.
Copyright (c) 2008 Softwell. All rights reserved.
"""
MAX_RETRY=10
RETRY_TIME=0.01
LOCK_TIME=2
MSG_DEFAULT_EXPIRY=10


class GnrMessageHandler(object):
    """
    Message handler that uses gnrshareddata.
    There are 3 types of message:
    U-user       :Messages for an user
    C-connection :Messages for one connection
    P-page       :Messages for one page
    Any message is posted at a specific address composed by the prefix
    'MSG', the message type, the destination and a counter.For instance :
    MSG-U-jbrown-5 is the message n.5 for the user jbrown.
    MSG-P-cXhSPJ0BMfGs0vCBSk7Fag-34 is trhe message 34 for a page.
    For any possible address there are also 2 locations used to store
    messages written and read.
    So we will have also for instance the location MSG-U-jbrown-W and
    MSG-U-jbrown-R that are the counters for jbrown messages.
    When a message is posted it is written in the shareddata and the 
    counter is incremented.
    Any message has an expiry time and a body.
    
    """

    def __init__(self, site):
        self.site = site
        self.sd=self.site.shared_data
 
    def _postMessage(self,msgtype,address,body,expiry):
        sd=self.site.shared_data
        address ='MSG-%s-%s'%(msgtype,address)
        with sd.locked(key=address,max_retry=MAX_RETRY,lock_time=LOCK_TIME,retry_time=RETRY_TIME):
            counter_w='%s_W' % address
            k=sd.incr(counter_w)
            if k is None:
                k=1
                sd.set(counter_w,k)
            key='%s_%i' % (address,k) 
            sd.set(key,body,expiry)
    
    def _getMessages(self,msgtype,address):
        sd=self.site.shared_data
        address ='MSG-%s-%s'%(msgtype,address)
        result=[]
        with sd.locked(key=address,max_retry=MAX_RETRY,lock_time=LOCK_TIME,retry_time=RETRY_TIME):
            cnt=sd.get_multi(['R','W'],'%s_' % address)
            print cnt
            r_msg=cnt.get('R',0)
            w_msg=cnt.get('W',0)
            print 'r_msg:%i    -   w_msg:%i' % (r_msg,w_msg)
            if w_msg>r_msg:
                messages=sd.get_multi([str(k+1) for k in range(r_msg,w_msg)],'%s_' % address)
                print messages
                result=[messages.get(str(k+1)) for k in range(r_msg,w_msg)]
                sd.set('%s_R' % address,w_msg)
        return result
        
    def postPageMessage(self, page_id, body, expiry=MSG_DEFAULT_EXPIRY):
        return self._postMessage('P',page_id,body,expiry=expiry)
        
    def postUserMessage(self, username, body, expiry=MSG_DEFAULT_EXPIRY):
        return self._postMessage('U', username, body, expiry=expiry)

    def postConnectionMessage(self, connection_id, body, expiry=MSG_DEFAULT_EXPIRY):
        return self._postMessage('C', connection_id, body, expiry=expiry)
            
    def getPageMessages(self,page_id):
        return self._getMessages('P', page_id)
        
    def getUserMessages(self,username):
        return self._getMessages('U', username)
        
    def getConnectionMessages(self, connection_id):
        return self._getMessages('C', connection_id)
        
            
    
    
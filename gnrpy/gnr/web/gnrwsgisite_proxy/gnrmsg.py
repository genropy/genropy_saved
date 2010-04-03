#!/usr/bin/env python
# encoding: utf-8
"""
Created by Softwell on 2008-07-10.
Copyright (c) 2008 Softwell. All rights reserved.
"""



class GnrMessageHandler(object):
    
    def __init__(self, site):
        self.site = site
        
    def postPageMessage(self,page_id,body):
        pass
        
    def postUserMessage(self,username,body):
        pass
        
    def postConnectionMessage(self,connection_id,body):
        pass
            
    def getPageMessages(self,page_id):
        pass
        
    def getUserMessages(self,username):
        pass
        
    def getConnectionMessages(self,connection_id):
        pass
            
    
    
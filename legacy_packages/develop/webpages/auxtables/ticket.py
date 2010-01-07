#!/usr/bin/env python
# encoding: utf-8
"""
Created by Softwell on 2008-07-10.
Copyright (c) 2008 Softwell. All rights reserved.
"""

import os
from gnr.core.gnrbag import Bag

# --------------------------- GnrWebPage Standard header ---------------------------
class GnrCustomWebPage(object):
    maintable='develop.ticket'
    py_requires='public:Public,standard_tables:TableHandler,public:IncludedView'

######################## STANDARD TABLE OVERRIDDEN METHODS ###############
    def windowTitle(self):
        return '!!'
         
    def pageAuthTags(self, method=None, **kwargs):
        return 'user'
        
    def tableWriteTags(self):
        return 'user'
        
    def tableDeleteTags(self):
        return 'user'
        
    def barTitle(self):
        return '!!'
        
    def columnsBase(self,):
        return """"""
                  
            
    def orderBase(self):
        return ''
        
    def conditionBase(self):
        pass
    
    def queryBase(self):
        return dict(column='',op='contains', val='%')

############################## FORM METHODS ##################################

    def formBase(self, parentBC,disabled=False, **kwargs):
        pass
    
############################## RPC_METHODS ###################################       

# --------------------------- GnrWebPage Standard footer ---------------------------
def index(req, **kwargs):
    return GnrWebPage(req, GnrCustomWebPage, __file__, **kwargs).index()
        
#!/usr/bin/env python
# encoding: utf-8
"""
Created by Softwell on 2008-07-10.
Copyright (c) 2008 Softwell. All rights reserved.
"""

import os
from gnr.web.gnrwebpage import GnrWebPage
from gnr.core.gnrbag import Bag

# --------------------------- GnrWebPage Standard header ---------------------------
class GnrCustomWebPage(object):
    maintable='develop.client'
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
        
    def columnsBase(self):
        return """company,address,phones,emails"""
    
    def queryBase(self):
        return dict(column='',op='contains', val='%')

############################## FORM METHODS ##################################

    def formBase(self, parentBC,disabled=False, **kwargs):
        pane = parentBC.contentPane(margin='5px',**kwargs)
        fb = pane.formbuilder(cols=1, border_spacing='6px',disabled=disabled)
        fb.field('',width='',lbl='')
    
############################## RPC_METHODS ###################################       

# --------------------------- GnrWebPage Standard footer ---------------------------
def index(req, **kwargs):
    return GnrWebPage(req, GnrCustomWebPage, __file__, **kwargs).index()
        
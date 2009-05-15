#!/usr/bin/env python
# encoding: utf-8
"""
Created by Softwell on 2008-07-10.
Copyright (c) 2008 Softwell. All rights reserved.
"""

import os
from gnr.web.gnrwebpage import GnrWebPage
from gnr.core.gnrbag import Bag
from datetime import datetime

# --------------------------- GnrWebPage Standard header ---------------------------
class GnrCustomWebPage(object):
    maintable='invc.product'
    py_requires='public:Public,standard_tables:TableHandler,public:IncludedView'

######################## STANDARD TABLE OVERRIDDEN METHODS ###############
    def windowTitle(self):
        return '!!Products'
         
    def pageAuthTags(self, method=None, **kwargs):
        return 'user'
        
    def tableWriteTags(self):
        return 'user'
        
    def tableDeleteTags(self):
        return 'user'
        
    def barTitle(self):
        return '!!Products'
        
    def columnsBase(self,):
        return """code/Code:6,description"""
                  
            
    def orderBase(self):
        return 'code'
        
    def conditionBase(self):
        pass
    
    def queryBase(self):
        return dict(column='code',op='contains', val='%', runOnStart=True)

############################## FORM METHODS ##################################

    def formBase(self, parentBC,disabled=False, **kwargs):
        pane=parentBC.contentPane(padding='4em', **kwargs)
        fb=pane.formbuilder(cols=2, border_spacing='6px',disabled=disabled)
        fb.field('code',readOnly=True)
        fb.field('description')
        fb.field('product_type')
        pane.dataFormula("form.title", "code+'-'+description",code="^.code",description="^.description")
 
############################## RPC_METHODS ###################################       


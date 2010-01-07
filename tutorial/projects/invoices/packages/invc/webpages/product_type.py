#!/usr/bin/env python
# encoding: utf-8
"""
Created by Softwell on 2008-07-10.
Copyright (c) 2008 Softwell. All rights reserved.
"""
class GnrCustomWebPage(object):
    maintable='invc.product_type'
    py_requires='public:Public,standard_tables:TableHandler'

######################## STANDARD TABLE OVERRIDDEN METHODS ###############
    def windowTitle(self):
        return '!!Product Type'
         
    def pageAuthTags(self, method=None, **kwargs):
        return 'user'
        
    def tableWriteTags(self):
        return 'user'
        
    def tableDeleteTags(self):
        return 'user'
        
    def barTitle(self):
        return '!!Product Type'
        
    def columnsBase(self,):
        return """code,description"""
            
    def orderBase(self):
        return 'code'
        
    def conditionBase(self):
        pass
    
    def queryBase(self):
        return dict(column='description',op='contains', val='%')

############################## FORM METHODS ##################################

    def formBase(self, parentBC,disabled=False, **kwargs):
        pane=parentBC.contentPane(padding='4em', **kwargs)
        fb=pane.formbuilder(cols=2, border_spacing='6px',disabled=disabled)
        fb.field('code',width='5em')
        fb.field('description',width='15em')
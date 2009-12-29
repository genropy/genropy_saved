#!/usr/bin/env python
# encoding: utf-8
"""
Created by Softwell on 2008-07-10.
Copyright (c) 2008 Softwell. All rights reserved.
"""
# --------------------------- GnrWebPage Standard header ---------------------------
class GnrCustomWebPage(object):
    maintable='libcd.cd'
    py_requires='public:Public,standard_tables:TableHandler,public:IncludedView'

######################## STANDARD TABLE OVERRIDDEN METHODS ###############
    def windowTitle(self):
        return '!!Cd'
         
    def pageAuthTags(self, method=None, **kwargs):
        return ''
        
    def tableWriteTags(self):
        return ''
        
    def tableDeleteTags(self):
        return ''
        
    def barTitle(self):
        return '!!Cd'
        
    def columnsBase(self,):
        return """@album.title,price"""
            
    def orderBase(self):
        return ''
        
    def conditionBase(self):
        pass
    
    def queryBase(self):
        return dict(column='@album.title',op='contains', val='%')

############################## FORM METHODS ##################################

    def formBase(self, parentBC,disabled=False, **kwargs):
        pane = parentBC.contentPane(**kwargs)
        fb = pane.formbuilder(cols=2,border_spacing='4px',disabled=disabled)
        fb.field('album')
        fb.field('price')
    def onLoading(self,record,newrecord,loadingParameters,recInfo):
        self.debugger()
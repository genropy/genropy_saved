#!/usr/bin/env python
# encoding: utf-8
"""
Created by Softwell on 2008-07-10.
Copyright (c) 2008 Softwell. All rights reserved.
"""
class GnrCustomWebPage(object):
    maintable='libcd.album'
    py_requires='public:Public,standard_tables:TableHandler,public:IncludedView'

######################## STANDARD TABLE OVERRIDDEN METHODS ###############
    def windowTitle(self):
        return '!!Album'
         
    def pageAuthTags(self, method=None, **kwargs):
        return ''
        
    def tableWriteTags(self):
        return ''
        
    def tableDeleteTags(self):
        return ''
        
    def barTitle(self):
        return '!!Album'
        
    def columnsBase(self,):
        return """year,title,rating"""
            
    def orderBase(self):
        return 'title'
        
    def conditionBase(self):
        pass
    
    def queryBase(self):
        return dict(column='title',op='contains', val='%')

############################## FORM METHODS ##################################

    def formBase(self, parentBC,disabled=False, **kwargs):
        pane = parentBC.contentPane(**kwargs)
        fb = pane.formbuilder(cols=2,border_spacing='4px',disabled=disabled)
        fb.field('title')
        fb.field('year')
        fb.field('rating')
        fb.field('artist_id')
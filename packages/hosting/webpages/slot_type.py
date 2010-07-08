#!/usr/bin/env python
# encoding: utf-8

# untitled.py
# Created by Francesco Porcari on 2010-07-05.
# Copyright (c) 2010 Softwell. All rights reserved.

class GnrCustomWebPage(object):
    maintable='hosting.slot_type'
    py_requires='public:Public,standard_tables:TableHandlerLight,public:IncludedView'

######################## STANDARD TABLE OVERRIDDEN METHODS ###############
    def windowTitle(self):
        return '!!Slot type'
         
    def pageAuthTags(self, method=None, **kwargs):
        return 'user'
        
    def tableWriteTags(self):
        return 'user'
        
    def tableDeleteTags(self):
        return 'user'
        
    def barTitle(self):
        return '!!Slot type'
        
    def lstBase(self,struct):
        r = struct.view().rows()
        r.fieldcell('code', width='10em')
        r.fieldcell('description', width='20em')
        return struct    
            
    def orderBase(self):
        return 'code'
        
    def formBase(self,parentBC,disabled=None,**kwargs):
        pane = parentBC.contentPane(**kwargs)
        fb = pane.formbuilder(cols=3, border_spacing='4px',disabled=disabled,fld_width='10em')
        fb.field('code')
        fb.field('description',colspan=2)
   
#!/usr/bin/env python
# encoding: utf-8
"""
Created by Softwell on 2008-07-10.
Copyright (c) 2008 Softwell. All rights reserved.
"""
class GnrCustomWebPage(object):
    maintable='base.role'
    py_requires='public:Public,standard_tables:TableHandler,public:IncludedView'

######################## STANDARD TABLE OVERRIDDEN METHODS ###############
    def windowTitle(self):
        return '!!Role'
         
    def pageAuthTags(self, method=None, **kwargs):
        return 'admin'
        
    def tableWriteTags(self):
        return 'admin'
        
    def tableDeleteTags(self):
        return 'admin'
        
    def barTitle(self):
        return '!!Role'
        
    def columnsBase(self,):
        return """description"""
            
    def orderBase(self):
        return 'description'
        
    def conditionBase(self):
        pass
    
    def queryBase(self):
        return dict(column='description',op='contains', val='%')

############################## FORM METHODS ##################################

    def formBase(self, parentBC,disabled=False, **kwargs):
        pane = parentBC.contentPane(margin='5px',_class='pbl_roundedGroup',**kwargs)
        pane.div('Role',_class='pbl_roundedGroupLabel')
        fb = pane.formbuilder(cols=1,border_spacing='4px',disabled=disabled)
        fb.field('description',autospan=1)
#!/usr/bin/env python
# encoding: utf-8

# dev_lang.py
# Created by Francesco Porcari on 2011-03-24.
# Copyright (c) 2011 Softwell. All rights reserved.

class GnrCustomWebPage(object):
    maintable='devlang.dev_lang'
    py_requires='public:Public,standard_tables:TableHandler,public:IncludedView'

######################## STANDARD TABLE OVERRIDDEN METHODS ###############
    def windowTitle(self):
        return '!!Dev lang'
        
    def barTitle(self):
        return '!!Dev lang'
        
    def lstBase(self,struct):
        r = struct.view().rows()
        r.fieldcell('id')
        r.fieldcell('developer_id')
        r.fieldcell('language_id')
        r.fieldcell('_row_counter')        
        return struct
            
    def orderBase(self):
        return '_row_counter'
        
    def conditionBase(self):
        pass
    
    def queryBase(self):
        return dict(column='developer_id',op='contains', val='%')

    def formBase(self,parentBC,disabled=False,**kwargs):
        pass

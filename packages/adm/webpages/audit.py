#!/usr/bin/env python
# encoding: utf-8

# audit.py
# Created by Francesco Porcari on 2011-02-03.
# Copyright (c) 2011 Softwell. All rights reserved.

class GnrCustomWebPage(object):
    maintable='adm.audit'
    py_requires='public:Public,standard_tables:TableHandler,public:IncludedView'

######################## STANDARD TABLE OVERRIDDEN METHODS ###############
    def windowTitle(self):
        return '!!Audit'
         
    def pageAuthTags(self, method=None, **kwargs):
        return 'user'
        
    def tableWriteTags(self):
        return 'user'
        
    def tableDeleteTags(self):
        return 'user'
        
    def barTitle(self):
        return '!!Audit'
        
    def columnsBase(self):
        return 'tablename:20%,event:5%,record_pkey:10%,version:5%,data:40%'
            
    def orderBase(self):
        return '$tablename'
        
    def conditionBase(self):
        pass
    
    def queryBase(self):
        return dict(column='tablename',op='contains', val='%')

    def formBase(self,parentBC,disabled=False,**kwargs):
        pass

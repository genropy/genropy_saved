#!/usr/bin/env python
# encoding: utf-8

# ${TM_NEW_FILE_BASENAME}.py
# Created by ${TM_FULLNAME} on ${TM_DATE}.
# Copyright (c) ${TM_YEAR} ${TM_ORGANIZATION_NAME}. All rights reserved.

class GnrCustomWebPage(object):
    maintable=''
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
#!/usr/bin/env python
# encoding: utf-8

# item_category.py
# Created by Saverio Porcari on 2010-10-15.
# Copyright (c) 2010 __MyCompanyName__. All rights reserved.

class GnrCustomWebPage(object):
    maintable='flib.item'
    py_requires='public:Public,standard_tables:TableHandler,public:IncludedView'

######################## STANDARD TABLE OVERRIDDEN METHODS ###############
    def windowTitle(self):
        return '!!File Items'
         
    def pageAuthTags(self, method=None, **kwargs):
        return 'user'
        
    def tableWriteTags(self):
        return 'user'
        
    def tableDeleteTags(self):
        return 'user'
        
    def barTitle(self):
        return '!!File Items'
        
    def lstBase(self, struct):
        r = struct.view().rows()
        r.fieldcell('__ins_ts', name='!!Inserted on', width='8em')
        r.fieldcell('title', name='!!Title', width='8em')
        r.fieldcell('description', name='!!Description', width='18em')
        r.fieldcell('url', name='Url', width='10em')
        
                  
            
    def orderBase(self):
        return '__ins_ts'
        
    def conditionBase(self):
        pass
    
    def queryBase(self):
        return dict(column='title',op='contains', val='%')
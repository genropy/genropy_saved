#!/usr/bin/env python
# encoding: utf-8
"""
Created by Softwell on 2008-07-10.
Copyright (c) 2008 Softwell. All rights reserved.
"""
# --------------------------- GnrWebPage Standard header ---------------------------
class GnrCustomWebPage(object):
    maintable='adm.connection'
    py_requires='public:Public,standard_tables:TableHandler,public:IncludedView'

######################## STANDARD TABLE OVERRIDDEN METHODS ###############
    def windowTitle(self):
        return '!!Connection'
         
    def pageAuthTags(self, method=None, **kwargs):
        return 'admin'
        
    def tableWriteTags(self):
        return 'none'
        
    def tableDeleteTags(self):
        return 'admin'
        
    def barTitle(self):
        return '!!Connection'
        
    def lstBase(self):
        struct = self.newGridStruct()
        r = struct.view().rows()
        r.fieldcell('username',width='10em',name='Username')
        r.fieldcell('user_fullname',width='10em',name='User name')

        r.fieldcell('start_ts',width='20em',name='!!Connection start')
        r.fieldcell('end_ts',width='20em',name='!!Connection end')
        r.fieldcell('end_reason',width='20em',name='!!End reason')
        r.fieldcell('ip',width='10em',name='!!Remote addr.')
        r.fieldcell('user_agent',width='30em')

        return struct
            
    def orderBase(self):
        return 'username'
        
    def conditionBase(self):
        pass
    
    def queryBase(self):
        return dict(column='username',op='contains', val='%')

############################## FORM METHODS ##################################

    def formBase(self, parentBC,disabled=False, **kwargs):
        bc = parentBC.borderContainer(**kwargs)
        iv = self.includedViewBox(bc,label='!!Served pages',
                            storepath='.@adm_served_page_connection_id', struct=self.served_page_struct(),
                             autoWidth=True)
        gridEditor = iv.gridEditor()
        
    def served_page_struct(self):
        struct = self.newGridStruct()
        r = struct.view().rows()
        r.cell('page_id',name='Served Page ID',width='20em')
        r.fieldcell('start_ts',name='Start',width='10em')
        r.fieldcell('end_ts',name='End',width='10em')
        r.fieldcell('end_reason',name='End reason',width='10em')
        r.cell('pagename',name='Page name',width='15em')
        r.cell('subscribed_tables',name='Subscribed table',width='20em')
        return struct
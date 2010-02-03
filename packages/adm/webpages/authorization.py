#!/usr/bin/env python
# encoding: utf-8
"""
Created by Softwell on 2008-07-10.
Copyright (c) 2008 Softwell. All rights reserved.
"""

# --------------------------- GnrWebPage Standard header ---------------------------
class GnrCustomWebPage(object):
    maintable='adm.authorization'
    py_requires='public:Public,standard_tables:TableHandlerLight'

######################## STANDARD TABLE OVERRIDDEN METHODS ###############
    def windowTitle(self):
        return '!!Authorization'
         
    def pageAuthTags(self, method=None, **kwargs):
        return 'admin'
        
    def tableWriteTags(self):
        return 'admin'
        
    def tableDeleteTags(self):
        return 'admin'
        
    def barTitle(self):
        return '!!Authorization'
        
    def lstBase(self,struct):
        r = struct.view().rows()
        r.fieldcell('@user_id.username',width='15em',name='!!Created by')
        r.fieldcell('note',width='30em')
        r.fieldcell('code',width='6em')
        r.fieldcell('used_by',name='Used by',width='8em')
        r.fieldcell('use_ts',name='Use date',width='8em')
        return struct
                  
    def orderBase(self):
        return '@user_id.username'
        
    def conditionBase__(self):
        return ('$use_ts IS NULL',{})
 
############################## FORM METHODS ##################################

    def formBase(self, parentBC,disabled=False, **kwargs):
        pane = parentBC.contentPane(**kwargs)
        fb = pane.formbuilder(cols=1, border_spacing='4px',disabled=disabled)
        fb.textbox(value='^.code',lbl='!!Code',readOnly=True,font_size='2em',ghost='!!To be created')
        fb.simpleTextArea(value='^.note',lbl='!!Note',height='10ex',width='100%')
        
    def onSaving(self, recordCluster, recordClusterAttr, resultAttr):
        recordCluster['code'] = self.tblobj.generate_code()
        recordCluster['user_id'] = self.userRecord('id')
        
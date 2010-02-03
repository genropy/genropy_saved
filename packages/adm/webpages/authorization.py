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
        r.fieldcell('@user_id.username',width='15em',name='!!By')
        r.fieldcell('auth_tag',width='15em')
        r.fieldcell('note',width='30em')
        r.fieldcell('code',width='6em',styles='display:block;')
        return struct
                  
    def orderBase(self):
        return '@user_id.username'
        
    def conditionBase(self):
        return ('$redeemed IS FALSE',{})
 
############################## FORM METHODS ##################################

    def formBase(self, parentBC,disabled=False, **kwargs):
        pane = parentBC.contentPane(**kwargs)
        fb = pane.formbuilder(cols=1, border_spacing='4px',disabled=disabled)
        fb.field('auth_tag',dbtable='adm.tag',hasDownArrow=True,tag='dbCombobox')
        fb.simpleTextArea(value='^.note',lbl='!!Note')
        fb.div('^.code')
        
    def onSaving(self, recordCluster, recordClusterAttr, resultAttr):
        recordCluster['code'] = self.tblobj.generate_code()
        recordCluster['user_id'] = self.userRecord('id')
        recordCluster['redeemed'] = False
        
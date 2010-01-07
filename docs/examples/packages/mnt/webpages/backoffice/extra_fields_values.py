#!/usr/bin/env python
# encoding: utf-8
"""
etcf.py

Created by Jeff B. Edwards on 2008-11-07.
Copyright (c) 2008 Goodsoftware Pty Ltd All rights reserved.
"""
import os
from gnr.core.gnrbag import Bag

# --------------------------- GnrWebPage subclass ---------------------------
class GnrCustomWebPage(object):
    maintable='mnt.jos_community_fields_values'
    py_requires='public:Public,standard_tables:TableHandler,public:IncludedView'

    def windowTitle(self):
        return '!!Valori Campi Extra'

    def pageAuthTags(self, method=None, **kwargs):
        return 'admin'
        
    def tableWriteTags(self):
        return 'admin'
        
    def tableDeleteTags(self):
        return 'admin'
        
    def barTitle(self):
        return '!!Valori Campi Extra'
        
    def columnsBase(self,):
        return """
                  id/Id:4,
                  @user_id.name/Utente:14,
                  @field_id.name/Campo:14,
                  value/Valore:14
               """

    def formBase(self, parentBC,  disabled=False, **kwargs):
        bc=parentBC.borderContainer(**kwargs)
        base= bc.contentPane(region='center', _class='pbl_roundedGroup',margin='5px')
        base.div('!!Valori Campi Extra',_class='pbl_roundedGroupLabel')
        fb = base.formbuilder(cols=1, margin_left='2em',border_spacing='7px',margin_top='1em',disabled=disabled)
        fb.field('mnt.jos_community_fields_values.user_id',width='24em')
        fb.field('mnt.jos_community_fields_values.field_id',width='24em')
        fb.field('mnt.jos_community_fields_values.value',width='24em')

    def orderBase(self):
        return '@user_id.name'
    
    def queryBase(self):
        return dict(column='@user_id.name',op='contains', val='%', runOnStart=False)

                               
def index(req, **kwargs):
    return GnrWebPage(req, GnrCustomWebPage, __file__, **kwargs).index()

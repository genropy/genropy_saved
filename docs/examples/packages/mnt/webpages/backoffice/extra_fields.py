#!/usr/bin/env python
# encoding: utf-8
"""
etcf.py

Created by Jeff B. Edwards on 2008-11-07.
Copyright (c) 2008 Goodsoftware Pty Ltd All rights reserved.
"""
import os
from gnr.web.gnrwebpage import GnrWebPage
from gnr.core.gnrbag import Bag

# --------------------------- GnrWebPage subclass ---------------------------
class GnrCustomWebPage(object):
    maintable='mnt.jos_community_fields'
    py_requires='public:Public,standard_tables:TableHandler,public:IncludedView'

    def windowTitle(self):
        return '!!Campi Extra'

    def pageAuthTags(self, method=None, **kwargs):
        return 'admin'
        
    def tableWriteTags(self):
        return 'admin'
        
    def tableDeleteTags(self):
        return 'admin'
        
    def barTitle(self):
        return '!!Campi Extra'
        
    def columnsBase(self,):
        return """
                  id/Id:4,
                  type/Tipo:14,
                  published/Pbl:3, 
                  min/Min:3, 
                  max/Max:3, 
                  name/Name:20,
                  tips/Tips:20, 
                  visible/Vis.:3, 
                  required/Req:3, 
                  searchable/Srch:3,
                  options/Opzioni:30, 
                  fieldcode/Codice:12     
               """
    def formBase(self, parentBC,  disabled=False, **kwargs):
        bc=parentBC.borderContainer(**kwargs)
        base= bc.contentPane(region='center', _class='pbl_roundedGroup',margin='5px')
        base.div('!!Campi Extra',_class='pbl_roundedGroupLabel')
        fb = base.formbuilder(cols=1, margin_left='2em',border_spacing='7px',margin_top='1em',disabled=disabled)
        fb.field('mnt.jos_community_fields.id',width='5em')
        fb.field('mnt.jos_community_fields.type',width='10em')
        fb.field('mnt.jos_community_fields.published',width='3em')
        fb.field('mnt.jos_community_fields.min',width='4em')
        fb.field('mnt.jos_community_fields.max',width='4em')
        fb.field('mnt.jos_community_fields.name',width='14em')
        fb.field('mnt.jos_community_fields.tips',width='30em')
        fb.field('mnt.jos_community_fields.visible',width='4em')
        fb.field('mnt.jos_community_fields.required',width='4em')
        fb.field('mnt.jos_community_fields.searchable',width='4em')
        fb.field('mnt.jos_community_fields.options',width='40em',tag='simpletextarea')
        fb.field('mnt.jos_community_fields.fieldcode',width='10em')
        
    def orderBase(self):
        return 'name'
    
    def queryBase(self):
        return dict(column='name',op='contains', val='%', runOnStart=False)

                               
def index(req, **kwargs):
    return GnrWebPage(req, GnrCustomWebPage, __file__, **kwargs).index()

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
    maintable='mnt.jos_content'
    py_requires='public:Public,standard_tables:TableHandler,public:IncludedView'

    def windowTitle(self):
        return '!!Contenuti'

    def pageAuthTags(self, method=None, **kwargs):
        return 'admin'
        
    def tableWriteTags(self):
        return 'admin'
        
    def tableDeleteTags(self):
        return 'admin'
        
    def barTitle(self):
        return '!!Contenuti'
        
    def columnsBase(self,):
        return """
                  id/Id:4,
                  title:14,
                  alias:14,
                  title_alias:14,
                  state:4,
                  sectionid:4,
                  mask:4,
                  catid:4,
                  created:4,
                  created_by:4,
                  created_by_alias:4,
                  modified:4,
                  modified_by:4,
                  checked_out:4,
                  checked_out_time:4,
                  publish_up:4,
                  publish_down:4,
                  images:4,
                  urls:4,
                  attribs:4,
                  version:4,
                  parentid:4,
                  ordering:4,
                  metakey:4,
                  metadesc:4,
                  access:4,
                  hits:4,
                  metadata:4
               """


    #           look to this url for info on formatting   http://www.unicode.org/reports/tr35/tr35-4.html#Date_Format_Patterns

    def formBase(self, parentBC,  disabled=False, **kwargs):
        bc=parentBC.borderContainer(**kwargs)
        base= bc.contentPane(region='center', _class='pbl_roundedGroup',margin='5px')
        base.div('!!ETCF',_class='pbl_roundedGroupLabel')
        fb = base.formbuilder(cols=1, margin_left='2em',border_spacing='7px',margin_top='1em',disabled=disabled)
        fb.field('mnt.jos_content.id',width='5em')
        fb.field('mnt.jos_content.title',width='24em')

    def orderBase(self):
        return 'title'
    
    def queryBase(self):
        return dict(column='title',op='contains', val='%', runOnStart=False)

                               
def index(req, **kwargs):
    return GnrWebPage(req, GnrCustomWebPage, __file__, **kwargs).index()

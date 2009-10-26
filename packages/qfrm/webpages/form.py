#!/usr/bin/env python
# encoding: utf-8
"""
form.py

Created by Jeff Edwards on 2009-01-21.
Copyright (c) 2008 Goodsoftware Pty Ltd All rights reserved.
"""
import os
#from gnr.web.gnrwebpage import GnrWebPage
from gnr.core.gnrbag import Bag

# --------------------------- GnrWebPage subclass ---------------------------
class GnrCustomWebPage(object):
    maintable='qfrm.form'
    py_requires='public:Public,standard_tables:TableHandler'

    def windowTitle(self):
        return '!!Form'

    def pageAuthTags(self, method=None, **kwargs):
        return 'user'
        
    def tableWriteTags(self):
        return 'user'
        
    def tableDeleteTags(self):
        return 'user'
        
    def barTitle(self):
        return '!!Definition'
        
    def columnsBase(self,):
        return """
                  pkg_table:10,
                  bag_field:10,
                  version:5,
                  short_name:10,
                  long_name:10,
                  cols:4,
                  rows:4,
                  css
               """
    #           look to this url for info on formatting   http://www.unicode.org/reports/tr35/tr35-4.html#Date_Format_Patterns

    def formBase(self, parentBC,  disabled=False, **kwargs):
        bc=parentBC.borderContainer(**kwargs)
        base= bc.contentPane(region='center', _class='pbl_roundedGroup',margin='5px')
        base.div('!!Form',_class='pbl_roundedGroupLabel')
        fb = base.formbuilder(cols=2, margin_left='2em',border_spacing='7px',margin_top='1em',disabled=disabled)
        fb.field('pkg_table',width='20em', colspan=2)
        fb.field('bag_field',width='20em', colspan=2)
        fb.field('version',width='20em', colspan=2)
        fb.field('sort_order',width='10',colspan=2)
        fb.field('short_name',width='20em', colspan=2)
        fb.field('long_name',width='30em',colspan=2)
        fb.field('cols',width='6em',colspan=1)
        fb.field('rows',width='6em',colspan=1)
        fb.simpleTextarea(lbl='CSS',value='^.css',lbl_vertical_align='top', width='30em', height='10em', colspan=2)

        
    def orderBase(self):
        return 'short_name'
    
    def queryBase(self):
        return dict(column='short_name',op='contains', val='%', runOnStart=True)



#!/usr/bin/env python
# encoding: utf-8
"""
definition.py

Created by Jeff Edwards on 2009-01-21.
Copyright (c) 2008 Goodsoftware Pty Ltd All rights reserved.
"""
import os
#from gnr.web.gnrwebpage import GnrWebPage
from gnr.core.gnrbag import Bag

# --------------------------- GnrWebPage subclass ---------------------------
class GnrCustomWebPage(object):
    maintable='qfrm.definition'
    py_requires='public:Public,standard_tables:TableHandler'

    def windowTitle(self):
        return '!!Definition'

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
                  code,
                  pkg_table,
                  short_name,
                  long_name,
                  cols,
                  rows,
                  css
               """
    #           look to this url for info on formatting   http://www.unicode.org/reports/tr35/tr35-4.html#Date_Format_Patterns

    def formBase(self, parentBC,  disabled=False, **kwargs):
        bc=parentBC.borderContainer(**kwargs)
        base= bc.contentPane(region='center', _class='pbl_roundedGroup',margin='5px')
        base.div('!!Definition',_class='pbl_roundedGroupLabel')
        fb = base.formbuilder(cols=2, margin_left='2em',border_spacing='7px',margin_top='1em',disabled=disabled)
        fb.field('code',width='8.5em', colspan=1)
        fb.field('pkg_table',width='8.5em', colspan=1)
        fb.field('short_name',width='30em', colspan=2)
        fb.field('long_name',width='20em',colspan=2)
        fb.field('cols',width='6em',colspan=1)
        fb.field('rows',width='6em',colspan=1)
        fb.simpleTextarea(lbl='CSS',value='^.css',lbl_vertical_align='top', width='30em', height='10em', colspan=2)

        
    def orderBase(self):
        return 'short_name'
    
    def queryBase(self):
        return dict(column='short_name',op='contains', val='%', runOnStart=True)

                               
def index(req, **kwargs):
    return GnrWebPage(req, GnrCustomWebPage, __file__, **kwargs).index()

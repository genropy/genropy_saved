#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  untitled
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#

""" staff """

from gnr.web.gnrwebpage import GnrWebPage
from gnr.core.gnrbag import Bag

# --------------------------- GnrWebPage subclass ---------------------------
class GnrCustomWebPage(object):
    maintable='adm.tag'
    py_requires = 'public:Public,standard_tables:TableHandler'
    def pageAuthTags(self, method=None, **kwargs):
        return 'admin'
        
    def windowTitle(self):
        return '!!Adm Tags'
        
    def barTitle(self):
        return '!!Tags'
        
    def tableWriteTags(self):
        return 'admin'
        
    def tableDeleteTags(self):
        return 'admin'
    
    def columnsBase(self):
        return """tagname:7,description:10,isreserved"""

    def formBase(self,parentBC,disabled=False,**kwargs):
        user = parentBC.contentPane(_class='pbl_roundedGroup',margin='5px',**kwargs)
        user.div('!!Manage Tags', _class='pbl_roundedGroupLabel')
        fb = user.formbuilder(cols=2, border_spacing='6px',disabled=disabled)
        fb.field('adm.tag.tagname',width='10em',lbl='!!Tagname')
        fb.field('adm.tag.isreserved',lbl='!!Reserved')
        fb.field('adm.tag.description',width='15em',colspan=2,
                 lbl='!!Description')


    def orderBase(self):
        return 'tagname'
    
    def queryBase(self):
        return dict(column='tagname',op='contains',val='%',runOnStart=True)
        
def index(req, **kwargs):
    return GnrWebPage(req, GnrCustomWebPage, __file__, **kwargs).index()

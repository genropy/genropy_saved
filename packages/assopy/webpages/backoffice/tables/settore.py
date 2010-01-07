#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  untitled
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#

""" Settori """

from gnr.core.gnrbag import Bag

# --------------------------- GnrWebPage subclass ---------------------------
class GnrCustomWebPage(object):
    maintable='assopy.settore'
    py_requires='basecomponent:Public,standard_tables:TableHandler'
    
    def windowTitle(self):
        return '!!Assopy Settori'
         
    def pageAuthTags(self, method=None, **kwargs):
        return 'socio'
        
    def tableWriteTags(self):
        return 'talkadmin,superadmin'
        
    def barTitle(self):
        return '!!Tabella Settori'
        
    def columnsBase(self):
        return """descrizione:20,descrizione_en:10"""

    def formBase(self,pane,disabled=False,datapath=''):
        fb = pane.formbuilder(datapath=datapath,cols=1, margin_left='2em',border_spacing='7px',margin_top='1em',disabled=disabled)
        fb.field('assopy.settore.descrizione')
        fb.field('assopy.settore.descrizione_en')
        
    def orderBase(self):
        return 'descrizione'    
    
    def queryBase(self):
        return dict(column='descrizione',op='contains', val=None)

def index(req, **kwargs):
    return GnrWebPage(req, GnrCustomWebPage, __file__, **kwargs).index()

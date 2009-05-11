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
    maintable='assopy.track'
    py_requires='basecomponent:Public,standard_tables:TableHandler'
    
    def windowTitle(self):
        return '!!Assopy Track'
         
    def pageAuthTags(self, method=None, **kwargs):
        return 'socio'
        
    def barTitle(self):
        return '!!Gestione Track'
        
    def columnsBase(self):
        return """codice:9,titolo:15"""

    def formBase(self,pane,datapath='',disabled=False):
        fb = pane.formbuilder(datapath=datapath,cols=1, margin_left='2em',border_spacing='7px',margin_top='1em',disabled=disabled)
        fb.field('assopy.track.codice')
        fb.field('assopy.track.titolo')

        
    def orderBase(self):
        return 'codice'
        
    
    def queryBase(self):
        return dict(column='titolo',op='contains', val=None)
    


def index(req, **kwargs):
    return GnrWebPage(req, GnrCustomWebPage, __file__, **kwargs).index()

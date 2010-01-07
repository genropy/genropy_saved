#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  untitled
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#

""" Evento """
import time
import os
from gnr.core.gnrbag import Bag

# --------------------------- GnrWebPage subclass ---------------------------
class GnrCustomWebPage(object):
    maintable='assopy.evento'
    py_requires='basecomponent:Public,standard_tables:TableHandler'
    
    def windowTitle(self):
        return '!!Assopy Eventi'
         
    def pageAuthTags(self, method=None, **kwargs):
        return 'admin'
        
    def columnsBase(self):
        return """codice:8,titolo:10,edizione:3,location:10,localita:10,data_inizio,data_fine"""
        
    def formBase(self,pane,disabled=False,datapath=''):
        fb = pane.formbuilder(datapath=datapath,cols=1, margin_left='2em',border_spacing='7px',margin_top='1em')
        fb.field('assopy.evento.codice')
        fb.field('titolo')
        fb.field('edizione')
        fb.field('descrizione', tag='textarea', width='40em')
        fb.field('homepage')
        fb.br()
        fb.field('data_inizio')
        fb.field('data_fine')
        fb.field('location', width='30em')
        fb.field('indirizzo',width='30em')
        fb.field('cap', width='5em')
        fb.field('localita',width='20em')
        fb.field('provincia')
    
    def orderBase(self):
        return 'titolo'
    
    def queryBase(self):
        return dict(column='titolo',op='contains', val=None)
                               
def index(req, **kwargs):
    return GnrWebPage(req, GnrCustomWebPage, __file__, **kwargs).index()

#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  untitled
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#

""" Localita """
import time
import os
from gnr.core.gnrbag import Bag

class GnrCustomWebPage(object):
    maintable='glbl.localita'
    py_requires='public:Public,standard_tables:TableHandler'
    def windowTitle(self):
        return u'!!Località'
         
    def pageAuthTags(self, method=None, **kwargs):
        return None
        
    def tableWriteTags(self):
        return None
        
    def tableDeleteTags(self):
        return None
        
    def barTitle(self):
        return u'!!Località'
        
    def columnsBase(self,):
        return """nome/Nome:17,
                  provincia/Prov:3,
                  prefisso_tel/Prefisso:8,
                  cap/CAP:5,
                  codice_istat/Istat:6,
                  codice_comune/Codice:4"""
               
    def formBase(self, parentBC, disabled=False, **kwargs):
        pane=parentBC.contentPane(padding='5px',**kwargs).div(_class='pbl_roundedGroup', height='100%')
        pane.div(u'!!Località',_class='pbl_roundedGroupLabel')
        fb = pane.formbuilder(cols=1, margin_left='2em',border_spacing='7px',margin_top='1em',disabled=disabled)
        fb.field('glbl.localita.nome', width='20em')
        fb.field('glbl.localita.provincia',width='3em')
        fb.field('glbl.localita.prefisso_tel',width='3em')
        fb.field('glbl.localita.cap',width='3em')
        fb.field('glbl.localita.codice_istat',width='7em')
        fb.field('glbl.localita.codice_comune',width='4em')

    def orderBase(self):
        return 'nome'
    
    def queryBase(self):
        return dict(column='nome',op='contains', val=None)
    
                      

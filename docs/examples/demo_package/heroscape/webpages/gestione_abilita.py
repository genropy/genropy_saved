#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  untitled
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#

""" Gestione unita """
import time
import os
from gnr.core.gnrbag import Bag

# --------------------------- GnrWebPage subclass ---------------------------
class GnrCustomWebPage(object):
    maintable='heroscape.abilita'
    py_requires='public:Public,standard_tables:TableHandler'
    css_requires='generali.css'
    def windowTitle(self):
        return '!!Heroscape'
         
    def pageAuthTags(self, method=None, **kwargs):
        return 'user'
        
    def tableWriteTags(self):
        return 'user'
        
    def tableDeleteTags(self):
        return 'user'
        
    def barTitle(self):
        return u'!!Gestione abilità'
        
    def columnsBase(self,):
        return """nome:10,
                  descrizione:25"""
                  

    def formBase(self,pane,datapath='',disabled=False):
        fb = pane.formbuilder(datapath=datapath,cols=1,
                              border_spacing='7px',margin_top='1em',
                              disabled=disabled)

        fb.field('heroscape.abilita.nome',width='20em',value='^.nome',disabled=disabled,
                  required=True, invalidMessage='!!Obbligatorio')
        
        fb.field('heroscape.abilita.descrizione',width='20em',value='^.descrizione',disabled=disabled,
                  required=True, invalidMessage='!!Obbligatorio')
        
        fb.textarea(lbl='Descrizione',value='^.descrizione',_class='abil_txt',nodeId='descrizione')
      

                      
        
        
        
       
        
        


    def orderBase(self):
        return 'costo'
    
    def queryBase(self):
        return dict(column='nome',op='contains', val=None)
                               
def index(req, **kwargs):
    return GnrWebPage(req, GnrCustomWebPage, __file__, **kwargs).index()
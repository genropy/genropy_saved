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
    maintable='heroscape.prodotto'
    py_requires='public:Public,standard_tables:TableHandler'
    css_requires='generali.css'
    def windowTitle(self):
        return '!!Heroscape'
         
    def pageAuthTags(self, method=None, **kwargs):
        return None
        
    def tableWriteTags(self):
        return None
        
    def tableDeleteTags(self):
        return None
        
    def barTitle(self):
        return u'!!Gestione unità'
        
    def columnsBase(self,):
        return """sigla:5,
                  nome:14,
                  anno:6,
                  scenario:6"""
                  

    def formBase(self,pane,datapath='',disabled=False):
        form = pane.formbuilder(datapath=datapath,cols=3,
                              border_spacing='7px',margin_top='1em',
                              disabled=disabled)
        form.field('heroscape.prodotto.nome',width='12em',disabled=disabled,
                  required=True, invalidMessage='!!Obbligatorio')
        
        form.field('heroscape.prodotto.sigla',width='12em',disabled=disabled,
                  required=True, invalidMessage='!!Obbligatorio')
        
        form.field('heroscape.prodotto.anno',width='12em',disabled=disabled,
                  required=True, invalidMessage='!!Obbligatorio')
        
        form.field('heroscape.prodotto.descrizione',width='12em',disabled=disabled,
                  required=True, invalidMessage='!!Obbligatorio')
        
        form.field('heroscape.prodotto.scenario',width='12em',disabled=disabled,
                  required=True, invalidMessage='!!Obbligatorio')
        
     
                      
        
        
        
       
        
        


    def orderBase(self):
        return 'anno'
    
    def queryBase(self):
        return dict(column='nome',op='contains', val=None)
                               
def index(req, **kwargs):
    return GnrWebPage(req, GnrCustomWebPage, __file__, **kwargs).index()
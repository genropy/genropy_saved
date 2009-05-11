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
    maintable='assopy.oratore'
    py_requires='basecomponent:Public,standard_tables:TableHandler'

    def windowTitle(self):
        return '!!Assopy Oratori'
         
    def pageAuthTags(self, method=None, **kwargs):
        return 'socio'

    def barTitle(self):
        return '!!Gestione Oratore'
        
    def columnsBase(self):
        return """@anagrafica_id.@utente_id.nome_cognome,@anagrafica_id.cellulare,email:10,@utente.username"""
        

    def formBase(self,pane,disabled=False,datapath=''):
        fb = pane.formbuilder(datapath=datapath,cols=1, margin_left='2em',border_spacing='7px',margin_top='1em',disabled=disabled)
        fb.field('assopy.oratore.anagrafica_id')
        fb.field('assopy.oratore.attivita')
        fb.field('assopy.oratore.settore')
        fb.field('assopy.oratore.www')     
        fb.textarea(lbl_vertical_align='top', lbl='Descrizione',width='30em'
                    ,colspan=2,_class='form_textarea',value='^.descrizione')
    
    def orderBase(self):
        return '@anagrafica_id.@utente_id.nome_cognome'
    

    def queryBase(self):
        return dict(column='@anagrafica_id.@utente_id.nome_cognome',op='contains', val=None)


def index(req, **kwargs):
    return GnrWebPage(req, GnrCustomWebPage, __file__, **kwargs).index()

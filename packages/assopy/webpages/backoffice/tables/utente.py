#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  untitled
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#

""" staff """

from gnr.core.gnrbag import Bag

class GnrCustomWebPage(object):
    maintable='assopy.utente'
    py_requires='basecomponent:Public,standard_tables:TableHandler'
    
    def windowTitle(self):
        return '!!Assopy Utenti'
         
    def pageAuthTags(self, method=None, **kwargs):
        return 'socio'

    def barTitle(self):
        return '!!Gestione Utenti'
        
    def columnsBase(self):
        return """username:12,nome_cognome:12,email:15,data_registrazione/Registrato il:8,auth_tags:8,stato:8"""

    def formBase(self,pane,disabled,datapath=''):
        fb = pane.formbuilder(datapath=datapath,cols=1, margin_left='2em',border_spacing='7px',margin_top='1em',disabled=disabled)
        fb.field('assopy.utente.username')
        fb.field('assopy.utente.nome_cognome')
        fb.field('assopy.utente.email', width='30em')
        fb.field('assopy.utente.data_registrazione')
        fb.field('assopy.utente.stato')
        fb.field('assopy.utente.auth_tags',width='30em')

    def orderBase(self):
        return 'nome_cognome'

    
    def queryBase(self):
        return dict(column='nome_cognome',op='contains',val=None)
    

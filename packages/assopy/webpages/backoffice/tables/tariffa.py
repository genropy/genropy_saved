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

# --------------------------- GnrWebPage subclass ---------------------------
class GnrCustomWebPage(object):
    maintable='assopy.tariffa'
    py_requires='basecomponent:Public,standard_tables:TableHandler'
    
    def windowTitle(self):
        return '!!Assopy Tariffe'
         
    def pageAuthTags(self, method=None, **kwargs):
        return 'socio'

    def barTitle(self):
        return '!!Gestione Tariffe'
        
    def columnsBase(self):
        return """codice:10,descrizione:20,importo:10,aliquota_iva:10"""
    

    def formBase(self,pane,disabled=False,datapath=''):
        fb = pane.formbuilder(datapath=datapath,cols=1, margin_left='2em',border_spacing='7px',margin_top='1em',disabled=disabled)
        fb.field('assopy.tariffa.codice')
        fb.field('assopy.tariffa.descrizione')
        fb.field('assopy.tariffa.importo')
        fb.field('assopy.tariffa.tipo')
        fb.field('assopy.tariffa.decorrenza')
        fb.field('assopy.tariffa.scadenza')
        fb.field('assopy.tariffa.evento_id')
        fb.field('assopy.tariffa.aliquota_iva')
        fb.field('assopy.tariffa.ingressi_omaggio')
        fb.field('assopy.tariffa.prezzo_ivato')
        fb.field('assopy.tariffa.dicitura_it',width='40em')
        fb.field('assopy.tariffa.dicitura_en',width='40em')

        
    def orderBase(self):
        return 'descrizione'
        
    
    def queryBase(self):
        return dict(column='descrizione',op='contains', val=None)
    


def index(req, **kwargs):
    return GnrWebPage(req, GnrCustomWebPage, __file__, **kwargs).index()

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
    maintable='assopy.ordine'
    py_requires='basecomponent:Public,standard_tables:TableHandler'
    
    def windowTitle(self):
        return '!!Assopy Ordine'
         
    def pageAuthTags(self, method=None, **kwargs):
        return 'socio'

    def barTitle(self):
        return '!!Gestione Ordini'
        
    def columnsBase(self):
        return """numero:6,data_inserimento:7,data_conferma:7,data_pagamento:7,
                    fattura_data:7,fattura_num:6,@anagrafica_id.ragione_sociale:16"""
                    
    def formBase(self,pane,disabled=False,datapath=''):
        fb = pane.formbuilder(datapath=datapath,cols=2, margin_left='2em',border_spacing='7px',margin_top='1em',disabled=disabled)
        fb.field('assopy.ordine.numero')
        fb.field('assopy.ordine.tipo_protocollo')
        fb.field('assopy.ordine.tipo_ordine')
        fb.field('assopy.ordine.data_inserimento')
        fb.field('assopy.ordine.data_conferma')
        fb.field('assopy.ordine.data_pagamento')
        fb.field('assopy.ordine.evento_id')
        fb.field('assopy.ordine.anagrafica_id',lbl='Ragione sociale')
        fb.field('assopy.ordine.imponibile')
        fb.field('assopy.ordine.iva')
        fb.field('assopy.ordine.totale')
        fb.field('assopy.ordine.cond_pagamento')
        fb.field('assopy.ordine.fattura_num')
        fb.field('assopy.ordine.fattura_data')
        
        
    def orderBase(self):
        return 'numero'
        
    
    def queryBase(self):
        return dict(column='@anagrafica_id.ragione_sociale',op='contains', val=None)


def index(req, **kwargs):
    return GnrWebPage(req, GnrCustomWebPage, __file__, **kwargs).index()

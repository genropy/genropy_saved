#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  untitled
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#

""" Fatture """

from gnr.core.gnrbag import Bag

# --------------------------- GnrWebPage subclass ---------------------------
class GnrCustomWebPage(object):
    maintable='assopy.ordine'
    py_requires='basecomponent:Public,standard_tables:TableHandler'
    
    def windowTitle(self):
        return '!!Assopy Fatture'
         
    def pageAuthTags(self, method=None, **kwargs):
        return 'socio'

    def barTitle(self):
        return '!!Gestione Fatture'
    def tableWriteTags(self):
        return 'contabile,superadmin'
        
    def pluralRecordName(self):
        return '!!Fatture'
        
    def columnsBase(self):
        return """fattura_num:10,fattura_data:8,imponibile:8,iva:8,
                    totale:8,@anagrafica_id.ragione_sociale:16"""
                   
    def formBase(self,pane,disabled=False,datapath=''):
        lc=pane.layoutContainer(height='100%')
        bottom=lc.contentPane(layoutAlign='bottom',height='1.4em',background_color='#3272a6')
        bottom.a(href='^docsrc').div('!!Link diretto alla fattura',color='white',text_align='center')
        tc=lc.tabContainer(height='100%',layoutAlign='client')
        pane=tc.contentPane(title='Dati fattura')
        fb = pane.formbuilder(datapath=datapath,cols=2, margin_left='2em',border_spacing='7px',margin_top='1em',disabled=disabled)
        fb.field('assopy.ordine.fattura_num')
        fb.field('assopy.ordine.fattura_data')
        fb.field('assopy.ordine.anagrafica_id',lbl='Ragione sociale')
        fb.field('assopy.ordine.numero')
        fb.field('assopy.ordine.tipo_protocollo')
        fb.field('assopy.ordine.tipo_ordine')
        fb.field('assopy.ordine.data_inserimento')
        fb.field('assopy.ordine.data_conferma')
        fb.field('assopy.ordine.data_pagamento')
        fb.field('assopy.ordine.evento_id')
        fb.field('assopy.ordine.imponibile')
        fb.field('assopy.ordine.iva')
        fb.field('assopy.ordine.totale')
        fb.field('assopy.ordine.cond_pagamento')
        fb.field('assopy.ordine.cliente_rif')
        fb.br()
        fb.field('assopy.ordine.cliente_atn')
        fatt=tc.contentPane(title='Documento')
        fatt.dataScript('docsrc',"return genro.constructUrl('assopy/stampa_ordine.py/stampa',{locale:locale,ordine_id:ordine_id})",
        locale='=^form.record.@anagrafica_id.@utente_id.locale',
        ordine_id='^form.record.id',_if='ordine_id')
        
        fatt.iframe(border='0px',width='100%',height='100%',src='^docsrc')
        
        
        
    def orderBase(self):
        return 'numero'
        
    def conditionBase(self):
        return ('fattura_num IS NOT NULL',{})
    
    def queryBase(self):
        return dict(column='@anagrafica_id.ragione_sociale',op='contains', val=None)


def index(req, **kwargs):
    return GnrWebPage(req, GnrCustomWebPage, __file__, **kwargs).index()

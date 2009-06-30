#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-

import datetime

from gnr.web.gnrwebpage import GnrWebPage

class GnrCustomWebPage(object):
    def main(self, root, **kwargs):
        lc = root.layoutContainer(height='100%')
        top = lc.layoutContainer(layoutAlign='top', height='15ex', 
                         border_bottom='2px solid grey')
        top_left = top.contentPane(layoutAlign='left', width='22em', 
                         padding='20px', border_right='2px solid grey')
        top_right = top.contentPane(layoutAlign='client', padding='20px')
        main = lc.splitContainer(layoutAlign='client')
        left = main.contentPane(overflow='auto', sizeShare=30)
        right = main.splitContainer(orientation='vertical', sizeShare=70)
        right_top = right.contentPane(sizeShare=50)
        right_bottom = right.contentPane(sizeShare=50)
        self.recordSelect(top_left)
        self.dataModel(root)
        self.boxIndirizzo(top_right)
        self.boxRecordTree(left)
        self.boxOrdini(right_top)
        
    def recordSelect(self, pane):
        pane.dbSelect(value='^anagrafica.id', dbtable='assopy.anagrafica', width='20em', 
                            columns='ragione_sociale')
                           # auxColumns='localita,provincia,cap,codice_fiscale,partita_iva')
                            
    def dataModel(self, pane):
        pane.dataRecord('anagrafica.record', table='assopy.anagrafica', pkey='^anagrafica.id')
        
    def boxIndirizzo(self, pane):
        pane = pane.contentPane(datapath='anagrafica.record')
        
        pane.div('^.ragione_sociale', _class='mydiv')
        pane.div('^.indirizzo', _class='mydiv')
        ind = pane.div(_class='mydiv')
        ind.span('^.cap')
        ind.span('^.localita', mask=' %s ')
        ind.span('^.provincia', mask='(%s)')
        pane.div('^.@utente_id.email', _class='mydiv')
    
    def boxRecordTree(self, pane):
        pane.tree(storepath='anagrafica.record', inspect='shift', visible='^anagrafica.id')
        
    def boxOrdini(self, pane):
        struct = self.newGridStruct('assopy.ordine')
        r = struct.view().rows(classes='tablewiew_grid',
                        cellClasses='tablewiew_cells',headerClasses='tablewiew_headers')
        r.fieldcell('numero')
        r.fieldcell('tipo_ordine')
        r.fieldcell('data_inserimento')
        r.fieldcell('data_conferma')
        r.fieldcell('data_pagamento')
        r.fieldcell('fattura_num')
        pane.includedView(storepath='anagrafica.record.@assopy_ordine_anagrafica_id',
                                 struct=struct, selectedId='ordine.id')

        
def index(req, **kwargs):
    return GnrWebPage(req, GnrCustomWebPage, __file__, **kwargs).index()

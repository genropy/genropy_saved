#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  untitled
#
#  Created by Francesco Cavazzana on 2008-02-5.
#  Copyright (c) 2007 Softwell. All rights reserved.
#

""" modifica_utente """
import os
import datetime
from urllib import urlencode

from gnr.web.gnrwebpage import GnrWebPage
from gnr.core.gnrbag import Bag
from gnr.core.gnrstring import templateReplace, splitAndStrip

# #--------------------------- GnrWebPage subclass ---------------------------
class GnrCustomWebPage(object):
    maintable='assopy.ordine'
    py_requires='basecomponent:Public,shop:Shop,utils:SendMail'
    
    def windowTitle(self):
         return '!!Assopy Sponsorizzazione Pycon 2'
         
    def pageAuthTags(self, method=None, **kwargs):
        return 'users'
        
    def main(self, root, **kwargs):
        self.evento = self.eventoRecord()
        
        root.data('form.sponsorizzazione', True)
        root.data('tariffe.OMG', self.db.table('assopy.tariffa').record(evento_id=self.evento['id'], tipo='OMG', mode='record'))
        
        self.evento = self.eventoRecord()
        self.anagrafica = self.anagraficaRecord()
        top, pages = self.publicPagedPane(root, '!!Sponsorizzazione %s' % self.evento['titolo'], selected='selectedPage')
        #anagraficaOK = self.anagrafica and self.anagrafica['codice_fiscale']
        anagraficaOK = self.anagrafica 
        if anagraficaOK:
            self.pageIscrizione(pages)
            self.pageTrasferimento(pages)
            self.pagePrepBonifico(pages)
            self.pageOkBonifico(pages)
            self.pageSalvaBozza(pages)
            self.pageOkSalvaBozza(pages)
        else:
            self.pageNoAnag(pages)

    def pageIscrizione(self, pages):
        self.controllerIscrizione(pages)

        client, bottom = self.publicPage(pages, datapath='form')

        ordine = self.loadBozzaOrdine()
        client.data('form.ordine', ordine)

        lc = client.layoutContainer(height='100%')
        self.paneTotali(lc)

        main = lc.layoutContainer(layoutAlign='client')
        
        top = main.contentPane(layoutAlign='top', height='50px', border_bottom='1px solid grey')
        self.paneTop(top)
        
        slotspane = main.contentPane(layoutAlign='client')
        
        self.clientSlots(slotspane, ordine)

        self.payButtons(bottom)
        
    def paneTop(self, pane):
        pane.data('aux.rectariffa', dict(importo=0, ingressi_omaggio=0))
        pane.dataRecord('aux.rectariffa', 'assopy.tariffa', pkey='^.ordine.sponsorizzazione.tariffa_id', 
                       _onResult="""
                           var trec = GET aux.rectariffa;
                           SET .ordine.sponsorizzazione.tariffa_codice = trec.getItem('codice');
                           SET .ordine.sponsorizzazione.tariffa_descrizione = trec.getItem('descrizione');
                           
                           var importo = trec.getItem('importo');
                           if (!trec.getItem('prezzo_ivato')){
                                importo = importo * (1+(trec.getItem('aliquota_iva')/100));
                           }
                           SET .ordine.sponsorizzazione.importo = importo;
                           SET .ordine.sponsorizzazione.aliquota_iva = trec.getItem('aliquota_iva'); 
                           ordine.calcola(null);
                       """, _starter='^gnr.onStart', _if='pkey')

        
        fb = pane.formbuilder(cols=3)
        fb.dbSelect(lbl='Sponsorizzazione', width='16em', value='^.ordine.sponsorizzazione.tariffa_id', dbtable='assopy.tariffa', 
                    columns='$descrizione', order_by='$importo',
                    condition='$tipo = :spon', condition_spon='SPO'
                )
        
        fb.div('^aux.rectariffa.importo', lbl='Importo')
        fb.div('^aux.rectariffa.ingressi_omaggio', lbl='Ingressi Omaggio')

    def payButtons(self, pane):
        pane.div('!!Salva in bozza', connect_onclick='FIRE form.doSave="bozza"', _class='pbl_button', width='13em',float ='right')
        pane.div('!!Paga con bonifico', connect_onclick='FIRE form.doSave="bonifico"', _class='pbl_button', width='13em',float ='right')
        pane.div('!!Annulla',connect_onclick=self.cancel_url(), _class='pbl_button pbl_cancel',float='left')

    def loadBozzaOrdine(self):        
        anagrafica_id = self.anagraficaRecord('id')
        ordine = self.tblobj.ordineCorrente(anagrafica_id, 'SPO')
        if ordine:
            ordine = self.tblobj.dboLoad(record=ordine)
        else:
            ordine = self.tblobj.dboCreate(anagrafica_id=anagrafica_id, tipo_protocollo='T', tipo_ordine='SPO',
                                        data_inserimento=self.workdate, evento_id = self.evento['id'])
            rigaspon = self.db.table('assopy.ordine_riga').newrecord()
            ordine.setItem('sponsorizzazione', rigaspon)
        for k in range(len(ordine['children.ordine_riga']),10):
            ordine.setItem('children.ordine_riga.r_%i' % k, None) 
        return ordine
        
    def rpc_saveRecord(self, dbo, paymode, **kwargs):
        spons = dbo['sponsorizzazione']
                
        righe=dbo['children.ordine_riga']
        righe.setItem('r_%i' % len(righe), spons, _pkey=dbo.getAttr('sponsorizzazione', '_pkey')) 
        riga_ordine = dbo.pop('sponsorizzazione')
        
        invalid = self.tblobj.dboProcess(dbo)
        
        if invalid:
            return invalid

        for k, riga in righe.items():
            if not riga['tariffa_id']:
                righe.pop(k)
                
        
        if paymode != 'bozza':
            self.updateAvatar()
            dbo['mainrecord.data_conferma'] = self.workdate
            self.tblobj.aggiungiRigaPagamento(dbo, data_inserimento=self.workdate, mezzo = paymode)
            
        self.tblobj.dboExecute(dbo)
        self.db.commit()

        result = Bag()

        if paymode == 'paypal':
            result['paypalUrl'] = self._rpc_paypalUrl(dbo)
        elif paymode == 'bonifico':
            result['mailSent'] = self._rpc_inviaIstruzioniBonifico(dbo['mainrecord.id'])
        result['paymode'] = paymode
        return result        
            
def index(req, **kwargs):
    return GnrWebPage(req, GnrCustomWebPage, __file__, **kwargs).index()

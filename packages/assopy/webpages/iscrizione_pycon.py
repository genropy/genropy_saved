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
         return '!!Assopy Registrazione a Pycon 2'
         
    def pageAuthTags(self, method=None, **kwargs):
        return 'users'
        
    def main(self, root, **kwargs):
        self.evento = self.eventoRecord()
        root.dataScript('dummy','ordine.initDays(g1,g2,g3);ordine.calcola()',g1=u'!!Venerdì',g2=u'!!Sabato',g3=u'!!Domenica',starter='^gnr.onStart')
        root.data('form.sponsorizzazione', False)
        root.data('tariffe', self.db.table('assopy.tariffa').tariffeCorrenti(self.evento['id'], self.workdate, 'TK_%'))
        
        self.anagrafica = self.anagraficaRecord()
        top, pages = self.publicPagedPane(root, '!!Registrazione %s' % self.evento['titolo'], selected='selectedPage')
        anagraficaOK = self.anagrafica and self.anagrafica['codice_fiscale']
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

        pane = lc.contentPane(layoutAlign='client')

        self.clientSlots(pane, ordine)

        self.payButtons(bottom)
        
    def payButtons(self, pane):
        pane.dataScript('form.pagabile' ,'return ""', totale='^form.ordine.mainrecord.totale', _if='totale >0', _else='return "none"',_init=True)
        #pane.div('!!Salva in bozza', connect_onclick='FIRE form.doSave="bozza"', _class='pbl_button', width='13em',float ='right')
        pane.div('!!Paga con Paypal', connect_onclick='FIRE form.doSave="paypal"', _class='pbl_button',
                                       display='^form.pagabile', width='13em',float ='right')
                                       #tooltip='!!Se puoi paga con bonifico: ci risparmi le spese. Grazie')
        pane.div("!!Paga all'ingresso", connect_onclick='FIRE form.doSave="bonifico"', _class='pbl_button', 
                        tooltip=u"!!Da ora in avanti non sono più accettati pagamenti per bonifico.<br>Pertanto è possibile pagare con paypal oppure<br> direttamente per contanti all'ingresso",
                        display='^form.pagabile',width='18em',float ='right')
        pane.div('!!Annulla',connect_onclick=self.cancel_url(), _class='pbl_button pbl_cancel',float='left')
    
    def loadBozzaOrdine(self):
        anagrafica_id = self.anagraficaRecord('id')
        ordine = self.tblobj.ordineCorrente(anagrafica_id, 'TKT')
        if ordine:
            ordine = self.tblobj.dboLoad(record=ordine)
        else:
            ordine = self.tblobj.dboCreate(anagrafica_id=anagrafica_id, tipo_protocollo='T', tipo_ordine='TKT',
                                        data_inserimento=self.workdate, evento_id=self.evento['id'])
        for k in range(len(ordine['children.ordine_riga']),9):
            ordine.setItem('children.ordine_riga.r_%i' % k, None) 
        return ordine
        
    def rpc_saveRecord(self, dbo, paymode, **kwargs):
        invalid = self.tblobj.dboProcess(dbo)

        if invalid:
            return invalid

        righe=dbo['children.ordine_riga']
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

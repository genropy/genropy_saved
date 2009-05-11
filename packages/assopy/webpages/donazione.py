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
    py_requires='basecomponent:Public,utils:SendMail'
    
    def windowTitle(self):
         return '!!Assopy Donazione'
         
    def pageAuthTags(self, method=None, **kwargs):
        return 'users'

    def main(self, root, **kwargs):
        top, pages = self.publicPagedPane(root, '!!Donazione Python Italia APS', selected='selectedPage')
        self.anagrafica = self.anagraficaRecord()
        anagraficaOK = self.anagrafica and self.anagrafica['codice_fiscale']
        if anagraficaOK:
            self.pageDonazione(pages)
            self.pageTrasferimento(pages)
            self.pagePrepBonifico(pages)
            self.pageOkBonifico(pages)
        else:
            self.pageNoAnag(pages)

    def pageDonazione(self, pages):
        client, bottom = self.publicPage(pages, datapath='form')
        
        client.data('.ordine', self._loadRecord())

        lc = client.layoutContainer(height='100%')
        top = lc.layoutContainer(layoutAlign='top', height='100px')
        tr = top.contentPane(layoutAlign='right', width='18em', datapath='.ordine.related',
                                  border='1px solid #3272a6',margin='5px',padding='5px')
        tr.div('^.anagrafica.ragione_sociale')
        tr.div('^.anagrafica.indirizzo')
        tr.div(template=' ^.cap ^.localita (^.provincia)', datasource='^.anagrafica')
        tr.div(template='!!C.F.: ^.codice_fiscale', datasource='^.anagrafica')
        tr.div(template='!!P.IVA: ^partita_iva', datasource='^.anagrafica')
        
        tc = top.contentPane(layoutAlign='client')
        tc = top.div(padding='20px',innerHTML="""<object data="_resources/pycon-italia-blu.svg" type="image/svg+xml"></object>""")
            
        main = lc.contentPane(layoutAlign='client',datapath='.ordine.children.ordine_riga.r_0')
                
        fb = main.formbuilder(cols=1, margin='auto', margin='auto', margin_top='6em')
        fb.NumberSpinner(value='^.importo', lbl='!!Importo donazione', width='8em', required=True, autofocus=True,font_size='1.3em',
                         lbl_font_size='1.3em',text_align='right', currency='EUR', min=5, smallDelta=5, intermediateChanges=True)
        fb.dataFormula('form.aux.style', "'font-size:'+(14 + (importo / 3))+'px;text_align:center;margin-top:30px'", 
                           importo='^.importo',_init=True)

        btm = lc.contentPane(layoutAlign='bottom', height='60px')
        btm.div('', connect_onclick='FIRE form.doSave="paypal"', _class='pbl_button pbl_paypal', float ='right', margin_right='2em')
       
        bottom.div('!!Dona con Paypal', connect_onclick='FIRE form.doSave="paypal"', _class='pbl_button', width='13em',float ='right')
        bottom.div('!!Dona con bonifico', connect_onclick='FIRE form.doSave="bonifico"', _class='pbl_button', width='18em',float ='right')
        
        main.div("!!Grazie", style='^form.aux.style',margin='auto',_class='pbl_largemessage',margin_top='30px')



        client.dataScript('dummy', """if(paymode=='paypal'){
                                        SET selectedPage=1;
                                        
                                     } else {
                                        SET selectedPage=2;
                                     } 
                                     FIRE form.doSaveRecord=paymode;
                                     """,  importo='=.ordine.children.ordine_riga.r_0.importo',
                                     _if='importo>0',
                                     _else='alert("!!Importo non ammesso")',
                                     paymode='^form.doSave')
        
        client.dataRpc('form.saveResult', 'saveRecord', dbo='=.ordine', _POST=True, paymode='^form.doSaveRecord')
        
        client.dataScript('dummy', """if(paymode=='paypal'){
                                        genro.gotoURL(paypalUrl);
                                     } else {
                                        SET selectedPage=3;
                                     }""", paypalUrl='^form.saveResult.paypalUrl', paymode='=form.saveResult.paymode')
        

        
        
        
        bottom.div('Annulla',connect_onclick=self.cancel_url(), _class='pbl_button pbl_cancel',float='left')

    def pagePrepBonifico(self, pages):
        client,bottom=self.publicPage(pages,datapath='aux')
        client.div(u"!!Ti stiamo inviando le istruzioni per il bonifico...",_class='pbl_largemessage',margin='3em')

    def pageOkBonifico(self, pages):
        client,bottom=self.publicPage(pages,datapath='aux')
        client.div(u"!!Ti abbiamo inviato le istruzioni per il bonifico.",_class='pbl_largemessage',margin='3em')
        client.div(u"!!Ti preghiamo di seguire le istruzioni che troverai nella mail.",_class='pbl_largemessage',margin='3em')
        client.div(u"!!Grazie !",_class='pbl_largemessage',margin='3em')
        bottom.div(u'!!Torna al Menù',width='14em',connect_onclick=self.cancel_url(), _class='pbl_button pbl_cancel',float='right')

    def pageTrasferimento(self, pages):
        client,bottom=self.publicPage(pages,datapath='aux')
        client.div(u"!!Ti stiamo trasferendo a PayPal per il pagamento...",_class='pbl_largemessage',margin='3em')

    def _loadRecord(self, pkey=None, **kwargs):
        anagrafica_id = self.anagraficaRecord('id')
        
        if pkey:
            dbo = self.tblobj.dboLoad(pkey, anagrafica_id=anagrafica_id)
        else:
            dbo = self.tblobj.dboCreate(anagrafica_id=anagrafica_id, tipo_protocollo='D', tipo_ordine='DON',
                                        data_inserimento=self.workdate, data_conferma=self.workdate)
            
            tariffa_donazione = self.db.table('assopy.tariffa').record(codice='_DONAZ', mode='record')

            self.tblobj.aggiungiRiga(dbo, tariffa=tariffa_donazione, importo=5)
             
        return dbo
    
    def rpc_saveRecord(self, dbo, paymode, **kwargs):
        invalid = self.tblobj.dboProcess(dbo)
        if invalid:
            return invalid
        
        #try:
        if True:
            self.tblobj.aggiungiRigaPagamento(dbo, data_inserimento=self.workdate, mezzo = paymode)

            self.tblobj.dboExecute(dbo)
            self.db.commit()
        #except Exception, e:
        #    return self.application.errorAnalyze(e, caller=self, package=self.package)
        
        result = Bag()
        if paymode == 'paypal':
            result['paypalUrl'] = self._rpc_paypalUrl(dbo)
        else:
            result['mailSent'] =  self._rpc_inviaIstruzioniBonifico(dbo['mainrecord.id'])
        
        result['paymode'] = paymode
        return result
    
    def _rpc_inviaIstruzioniBonifico(self, idordine):
        recordBag = self.tblobj.record(idordine).output('bag')
        return self.sendMailTemplate('donate_bank.xml', self.userRecord('email'), recordBag)

        
    
    def _rpc_paypalUrl(self, dbo):
        #url = "https://www.paypal.com/cgi-bin/webscr"
        #url = "https://www.sandbox.paypal.com/cgi-bin/webscr"
        test_ipn = ('sandbox' in (self.userRecord('auth_tags') or ''))
        url = self.get_paypal_site(test_ipn) 
        
        anagrafica = dbo['related.anagrafica']
        ordine = dbo['mainrecord']
        pagamento =  dbo['children.pagamento.r_0']
        user = self.userRecord()
        
        nome, cognome = splitAndStrip(user['nome_cognome'], ' ', n=1, fixed=2)
        nazione = anagrafica['nazione'] or 'IT'
        if nazione == 'I': nazione = 'IT'
        
        params = dict(cmd='_donations',
                      #business='paypal@pycon.it',
                      business= self.get_paypal_business(test_ipn),
                      item_name="Donazione %s" % ordine['numero'],
                      invoice=ordine['numero'],
                      amount=ordine['totale'],
                      custom=pagamento['id'],
                      no_shipping='1',
                      no_note='1',
                      address_override='1', #non consente la modifica indirizzo
                      currency_code='EUR',
                      tax='0',
                      lc='IT',
                      bn='PP-DonationsBF',
                      
                      email=user['email'], 
                      first_name=nome, 
                      last_name=cognome,
                      address1=anagrafica['indirizzo'],
                      city=anagrafica['localita'],
                      state=anagrafica['provincia'],
                      zip=anagrafica['cap'],
                      country=nazione
                  )
        
        params = urlencode(params)        
        return '%s?%s' % (url, params)


    def pageNoAnag(self, pages):
        client,bottom=self.publicPage(pages,datapath='aux')
        if not self.anagrafica:
            client.div(u"!!Per effettuare una donazione è necessario completare il proprio profilo",_class='pbl_largemessage',margin='3em')
        else:
            client.div(u"!!Per effettuare una donazione è necessario completare il profilo con il Codice Fiscale",_class='pbl_largemessage',margin='3em')
        bottom.div(u'!!Completa il profilo', connect_onclick='genro.gotoURL("modifica_utente.py")',_class='pbl_button',float='right',width='13em')
        bottom.div(u'!!Torna al menù', connect_onclick='genro.gotoURL("index.py")',_class='pbl_button',float='right')

def index(req, **kwargs):
    return GnrWebPage(req, GnrCustomWebPage, __file__, **kwargs).index()

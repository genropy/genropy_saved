#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  untitled
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#

""" Season """
import os
from gnr.web.gnrwebpage import GnrWebPage
from gnr.core.gnrbag import Bag
from urllib import urlencode

from gnr.core.gnrstring import templateReplace,splitAndStrip


# --------------------------- GnrWebPage subclass ---------------------------
class Shop(object):
    def __onmixin__(self,**kwargs):
        self.js_requires.append('shop')
        
    def controllerIscrizione(self, pane):
        pane.dataScript('dummy', """if(paymode=='paypal'){
                                        SET selectedPage=1;
                                     } else if(paymode=='bonifico'){
                                        SET selectedPage=2;
                                     } else {
                                        SET selectedPage=4;
                                     }
                                      """, 
                                   paymode='^form.doSave')
        
        pane.dataRpc('form.saveResult', 'saveRecord', dbo='=form.ordine', 
                             _POST=True, paymode='^form.doRpcSave')
        
        pane.dataScript('dummy', """ordine.prepSave(paymode);
                                    FIRE form.doRpcSave = paymode;
                                    """, paymode='^form.doSave')
        
        pane.dataScript('dummy', """if(paymode=='paypal'){
                                        genro.gotoURL(paypalUrl);
                                     } else if(paymode=='bonifico') {
                                        SET selectedPage=3;
                                     } else {
                                        SET selectedPage=5;
                                     }
                                     """, paypalUrl='^form.saveResult.paypalUrl', paymode='=form.saveResult.paymode')

        
    def loadBozzaOrdine(self):
        return Bag()
        
    def pageIscrizione(self, pages):
        pass

    def paneTotali(self, pane):
        piede = pane.layoutContainer(layoutAlign='bottom', height='90px',border_top='1px solid #3272a6')
        datiCliente = piede.contentPane(layoutAlign='left', width='22em', datapath='.ordine.related', margin_left='10px',padding='2px', 
                                        font_size='0.97em',color='#3272a6')
        datiCliente.div('!!Fatturare a:', font_weight='bold')
        datiCliente.div('^.anagrafica.ragione_sociale')
        datiCliente.div('^.anagrafica.indirizzo')
        datiCliente.div(template="^.cap ^.localita (^.provincia)",datasource='^.anagrafica')
                                    
        datiCliente.div(template="!!C.F.: ^.codice_fiscale - P.IVA: ^.partita_iva", datasource='^.anagrafica')
  
        totali = piede.contentPane(layoutAlign='right', width='18em',border_left='1px solid #3272a6',color='#3272a6').formbuilder(cols=1,datapath='.ordine.mainrecord')
        totali.div('^aux.imponibile_txt',lbl='!!Imponibile',width='8em',text_align='right')
        totali.div('^aux.iva_txt',lbl='!!Iva',width='8em',text_align='right')
        totali.div('^aux.totale_txt',lbl='!!Totale',width='8em',text_align='right')
        
    def payButtons(self, pane):
        pass

    def clientSlots(self, pane, ordine):
        tickets = pane.div(datapath='.ordine.children.ordine_riga', _class='ordine_tickets tickets_hidden',id='tickets')
        for slotNum,riga in enumerate(ordine['children.ordine_riga'].values()):
            self.createSlot(tickets,riga,slotNum)
            
    def createSlot(self, tickets, riga, slotNum):
        dlgId='dlg_%i'% slotNum
        slot = tickets.div(_class='^.@cls', datapath='.r_%i' % slotNum, id='slot_%i'% slotNum,
                       onCreated="""dojo.connect(dojo.byId('edit_%i'),'onclick' ,genro.nodeById('drd_%i').widget,'_onDropDownClick');
                                    dojo.connect(dojo.byId('new_%i'),'onclick' ,genro.nodeById('drd_%i').widget,'_onDropDownClick')"""% (slotNum,slotNum,slotNum,slotNum))
        
        slot.dataFormula('.@cls', """'ordine_ticket ' + tariffa_tipo;""", tariffa_tipo='^.partecipante.tariffa_tipo', _init=True)
        
        onlyEmpty=slot.div(_class='onlyEmpty')
        onlyEmpty.div('!!Clicca per nuovo <br/> partecipante',id='new_%i' % slotNum, _class='ticket_new')
        onlyFilled=slot.div(_class='onlyFilled')
        up=onlyFilled.div()
        bar=up.div(height='18px')
        bar.div(_class='tiket_erase',connect_onclick="SET .partecipante=null;ordine.calcola(%i);" % slotNum,
                 tooltip='!!Elimina dati partecipante', hidden='=form.sponsorizzazione')
        bar.div(_class='tiket_edit', id='edit_%i' % slotNum, tooltip='!!Modifica dati partecipante')
        up.div(template='<b>^.nome ^.cognome</b>',font_size='1.1em', color='white',datasource='^.partecipante',text_align='center')
        up.div('^.partecipante.presenze',text_align='center',color='white',font_size='0.70em')
        up.div('^.tariffa_descrizione',margin_left='10px',margin_top='9px',color='#ffe566',font_size='0.80em',float='left', hidden='^form.sponsorizzazione')
        
        dright=onlyFilled.div(float='right',margin_top='4px')
        dright.span(u'€ ',font_size='1.6em',color='#ffe566',margin_right='5px', hidden='^form.sponsorizzazione')
        dright.span('^.importo',font_size='1.6em',color='#ffe566',margin_right='8px',margin_top='4px', hidden='^form.sponsorizzazione')

        tt=slot.div().dropdownbutton(nodeId='drd_%i'%slotNum,display='none').tooltipDialog(nodeId=dlgId,title='Partecipante',
                       onCreated="dojo.connect(widget,'onClose',function(){ordine.calcola(%i)})"%slotNum).div(background_color='#3272a6',datapath='.partecipante')
        titlebar=tt.div(_class='dlg_titlebar')
        titlebar.div(_class='dlg_titlebar_title')
        titlebar.div(_class='dlg_titlebar_icon',connect_onclick="genro.nodeById('%s').widget.onCancel()" % dlgId)
        fb = tt.formbuilder(cols=3, margin_top='3px',border_spacing='5px',lblclass='dlglabel',
                                  onEnter="genro.nodeById('%s').widget.onCancel()" % dlgId)
        fb.textbox(lbl='!!Nome',  colspan=3,value = '^.nome', width='16em', validate_len='2:', validate_case='c',
                                        invalidMessage='!!almeno 2 caratteri',_class='dlgfield')
        fb.textbox(lbl='!!Cognome', colspan=3, value = '^.cognome', width='16em', validate_len='2:', validate_case='c',
                               invalidMessage='!!almeno 2 caratteri',_class='dlgfield')
        
        fb.checkbox(lbl='!!Studente', value = '^.studente',margin_top='2px', hidden='=form.sponsorizzazione', lbl_hidden='=form.sponsorizzazione')
        fb.br()
        fb.horizontalslider(lbl='!!Esperienza', value = '^.py_level',margin_top='2px', 
                            discreteValues='5', width='100px', minimum=0, maximum=4)
        fb.div('^.@@py_level_dsc',style='font-style: italic;font-size: x-small; font-weight: normal;color:#ffe566;',width='130px')
        fb.dataScript('.@@py_level_dsc','return [l0,l1,l2,l3,l4][lv || 0]',l0=u"!!Nessuna",l1=u"!!Scarsa",l2=u"!!Discreta",
                                         l3=u"!!Buona",l4=u"!!Ottima",lv='^.py_level',_init=True)
        fb.br()
        s = fb.div(lbl='!!Presenza', colspan=3)
        #s=tt.div(align='center',colspan=2,margin_top='3px',padding='3px',border_top='1px solid white')
        label_style='display:inline; font-style: italic;font-size: x-small; font-weight: normal;color:#ffe566;'
        #s.span('!!Presenza: ')
        s.checkbox(u'!!Venerdì',value = '^.presenza_g1',label_style=label_style )
        s.checkbox('!!Sabato', margin_left='10px',value = '^.presenza_g2', label_style=label_style)
        s.checkbox('!!Domenica',margin_left='10px',value = '^.presenza_g3',label_style=label_style)

    def pageSalvaBozza(self, pages):
        client,bottom=self.publicPage(pages,datapath='aux')
        client.div(u"!!Salvataggio ordine in corso...",_class='pbl_largemessage',margin='3em')
        
    def pageOkSalvaBozza(self, pages):
        client,bottom=self.publicPage(pages,datapath='aux')
        client.div(u"!!L'ordine è stato salvato",_class='pbl_largemessage',margin='3em')
        client.div(u"!!Potrai richiamarlo in seguito per modificarlo e confermarlo",_class='pbl_largemessage',margin='3em')
        bottom.div(u'!!Torna al menù', connect_onclick=self.cancel_url(),_class='pbl_button',float='right')

    def pagePrepBonifico(self, pages):
        client,bottom=self.publicPage(pages,datapath='aux')
        #client.div(u"!!Ti stiamo inviando le istruzioni per il bonifico...",_class='pbl_largemessage',margin='3em')
        client.div(u"!!Ti stiamo inviando un promemoria per il pagamento.",_class='pbl_largemessage',margin='3em')
    def pageOkBonifico(self, pages):
        client,bottom=self.publicPage(pages,datapath='aux')
        #client.div(u"!!Ti abbiamo inviato le istruzioni per il bonifico.",_class='pbl_largemessage',margin='3em')
        client.div(u"!!Ti abbiamo inviato un promemoria per il pagamento.",_class='pbl_largemessage',margin='3em')
        client.div(u"!!Ti preghiamo di seguire le istruzioni che troverai nella mail.",_class='pbl_largemessage',margin='3em')
        client.div(u"!!Grazie !",_class='pbl_largemessage',margin='3em')
        bottom.div(u'!!Torna al menù', connect_onclick=self.cancel_url(),_class='pbl_button',float='right')
        

    def pageTrasferimento(self, pages):
        client,bottom=self.publicPage(pages,datapath='aux')
        client.div(u"!!Ti stiamo trasferendo a PayPal per il pagamento...",_class='pbl_largemessage',margin='3em')
        

        
    def _rpc_inviaIstruzioniBonifico(self, idordine):
        recordBag = self.tblobj.record(idordine).output('bag')
        return self.sendMailTemplate('pay_bank.xml', self.userRecord('email'), recordBag)
    
        
    
    def _rpc_paypalUrl(self, dbo):
        #url = "https://www.paypal.com/cgi-bin/webscr"
        test_ipn = ('sandbox' in (self.userRecord('auth_tags') or ''))
        url = self.get_paypal_site(test_ipn) 
        
        anagrafica = dbo['related.anagrafica']
        ordine = dbo['mainrecord']
        pagamento =  dbo['children.pagamento.r_0']
        user = self.userRecord()
        
        nome, cognome = splitAndStrip(user['nome_cognome'], ' ', n=1, fixed=2)
        nazione = anagrafica['nazione'] or 'IT'
        if nazione == 'I': nazione = 'IT'
        
        params = dict(cmd='_xclick',
                      #business='paypal@pycon.it',
                      business=self.get_paypal_business(test_ipn),
                      item_name="%s %s %s" % (len(dbo['children.ordine_riga']), self._('ingressi Pycon2'), ordine['numero']),
                      invoice=ordine['numero'],
                      amount=ordine['totale'],
                      custom=pagamento['id'],
                      no_shipping='1',
                      no_note='1',
                      address_override='1', #non consente la modifica indirizzo
                      currency_code='EUR',
                      tax='0',
                      lc='IT',
                      bn='PP-BuyNowBF',
                      
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
        result = '%s?%s' % (url, params)
        
        try:
            self.application.sendmail('test_pp@softwell.it', 'gporcari@softwell.it', 'url paypal', result)
        except:
            pass
        return result


    def pageNoAnag(self, pages):
        client,bottom=self.publicPage(pages,datapath='aux')
        if not self.anagrafica:
            client.div(u"!!Per iscriversi è necessario completare il proprio profilo",_class='pbl_largemessage',margin='3em')
        else:
            client.div(u"!!Per iscriversi è necessario completare il profilo con il Codice Fiscale",_class='pbl_largemessage',margin='3em')
        bottom.div(u'!!Completa il profilo',width='14em', connect_onclick='genro.gotoURL("modifica_utente.py")',_class='pbl_button',float='right',width='14em')
        bottom.div(u'!!Torna al menù', width='14em',connect_onclick='genro.gotoURL("index.py")',_class='pbl_button',float='right')
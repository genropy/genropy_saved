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

from gnr.core.gnrbag import Bag
from gnr.core.gnrstring import templateReplace, splitAndStrip

# #--------------------------- GnrWebPage subclass ---------------------------
class GnrCustomWebPage(object):
    maintable='assopy.ordine'
    py_requires='basecomponent:Public,shop:Shop,utils:SendMail'
    
    def windowTitle(self):
         return '!!Assopy Registrazione a Pycon 2'
         
    def pageAuthTags(self, method=None, **kwargs):
        return 'partecipanti'
        
    def main(self, root, **kwargs):
        self.evento = self.eventoRecord()
                
        self.anagrafica = self.anagraficaRecord()
        
        top, pages = self.publicPagedPane(root, '!!Gestione partecipanti %s' % self.evento['titolo'], selected='selectedPage')
        
        self.pagePartecipanti(pages)
        self.pageSalva(pages)
        self.pageOkSalva(pages)
            
    def pagePartecipanti(self, pages):
        client, bottom = self.publicPage(pages,datapath='aux')
        lc=client.layoutContainer(height='100%')
        notatop=lc.contentPane(layoutAlign='top',height='34px',background_color='#eee',padding='8px')
        client=lc.contentPane(layoutAlign='client')
        partecipanti = self.db.query('assopy.partecipante', columns='*', 
                                     where="""@ordine_riga_id.@ordine_id.anagrafica_id = :idanag 
                                          AND @ordine_riga_id.@ordine_id.evento_id = :idevento 
                                          AND @ordine_riga_id.@ordine_id.data_conferma IS NOT NULL
                                          """,
                                          idanag = self.anagrafica['id'],
                                          idevento = self.evento['id']
                     ).selection().output('recordlist')
        
        client.data('form.partecipanti', partecipanti)
        client.dataScript('dummy','ordine.initDays(g1,g2,g3);ordine.presenze_partecipanti()',g1=u'!!Venerdì',g2=u'!!Sabato',g3=u'!!Domenica',starter='^gnr.onStart')
        
        
        client.dataRpc('form.saveResult', 'savePartecipanti', partecipanti='=form.partecipanti', 
                             _POST=True, _fired='^form.doSave')
                             
        client.dataScript('dummy', """SET selectedPage=1;""", _fired='^form.doSave')
        client.dataScript('dummy', """SET selectedPage=2;""", _fired='^form.saveResult')
        notatop.div(u"!!Qui trovi tutti i partecipanti che sono collegati al tuo account",text_align='center',color='#3272a6',font_size='1.1em')
        notatop.div(u"!!Da qui potrai gestire i dati collegati e anche riservare i posti per la <a href='http://www.pycon.it/pycon2/pyfiorentina'>PyFiorentina</a> ",text_align='center',color='#3272a6',font_size='0.9em')
        
        tickets = client.div(datapath='form.partecipanti', _class='ordine_tickets',id='tickets')
        for slotNum,riga in enumerate(partecipanti.values()):
            self.createSlot(tickets,riga,slotNum)
        
        self.saveButtons(bottom)
        
    def saveButtons(self, pane):
        pane.div('!!Registra', connect_onclick='FIRE form.doSave=true', _class='pbl_button', width='13em',float ='right')
        pane.div('!!Annulla',connect_onclick=self.cancel_url(), _class='pbl_button pbl_cancel',float='left')
        
            
    def createSlot(self, tickets, riga, slotNum):
        dlgId='dlg_%i'% slotNum
        slot = tickets.div(_class='^.@cls', datapath='.r_%i' % slotNum, id='slot_%i'% slotNum,
                       onCreated="""dojo.connect(dojo.byId('edit_%i'),'onclick' ,genro.nodeById('drd_%i').widget,'_onDropDownClick');
                                    """% (slotNum,slotNum))
                                    
        slot.dataFormula('.@cls', """'ordine_ticket filled_ticket ' + tariffa_tipo;""", tariffa_tipo='^.tariffa_tipo', _init=True)
        
        onlyFilled=slot.div(_class='onlyFilled')
        up=onlyFilled.div()
        bar=up.div(height='12px')
        bar.div(_class='tiket_edit', id='edit_%i' % slotNum, tooltip='Modifica dati partecipante')
        up.div(margin_left='16px',template='<b>^.nome ^.cognome</b>',font_size='1.1em', color='white',datasource='^.#parent.r_%i' % slotNum,text_align='center')
        up.div(template='&nbsp;^.qualifica_badge',font_size='.8em', color='yellow',datasource='^.#parent.r_%i' % slotNum,text_align='center')
        
        up.div('^.presenze',text_align='center',color='white',font_size='0.70em',margin_top='4px')
        lastline=up.div(font_size='.7em',margin='7px')
        lastline.div('!!Esperienza:',float='left', color='white')
        lastline.div( '^.@@py_level_dsc',float='left',margin_left='3px',color='yellow')
        lastline.div( '^.@@py_ristorante_posti',float='right', color='yellow',default_value='0')
        lastline.div('^.@@py_ristorante_lbl',float='right',color='white',margin_right='3px')
        
        
        up.div('^.tariffa_descrizione',margin_left='10px',margin_top='9px',color='#ffe566',font_size='0.90em',float='left')
        
        dright=onlyFilled.div(float='right',margin_top='4px')
        
        tt=slot.div().dropdownbutton(nodeId='drd_%i'%slotNum,display='none').tooltipDialog(nodeId=dlgId,title='Partecipante',
                       onCreated="dojo.connect(widget,'onClose',function(){ordine.presenze_partecipanti(%i)})"%slotNum
                       ).div(background_color='#3272a6')
        titlebar=tt.div(_class='dlg_titlebar')
        titlebar.div(_class='dlg_titlebar_title')
        titlebar.div(_class='dlg_titlebar_icon',connect_onclick="genro.nodeById('%s').widget.onCancel()" % dlgId)
        fb = tt.formbuilder(cols=3, margin_top='3px',border_spacing='5px',lblclass='dlglabel',
                                  onEnter="genro.nodeById('%s').widget.onCancel()" % dlgId)

        fb.textbox(lbl='Nome',  colspan=3,value = '^.nome', width='16em', validate_len='2:', validate_case='c',
                               invalidMessage='!!almeno 2 caratteri',_class='dlgfield')
        
        fb.textbox(lbl='Cognome', colspan=3, value = '^.cognome', width='16em', validate_len='2:', validate_case='c',
                               invalidMessage='!!almeno 2 caratteri',_class='dlgfield')
        fb.textbox(lbl='!!Qualifica sul badge', colspan=3, value = '^.qualifica_badge', 
                     tooltip=u'!!Indicare la qualifica che verrà stampata sul badge.<br/>Ad esempio <b>Programmatore alla Foo.srl</b><br/>oppure <b>Sviluppatore indipendente</b><br/>o ciò che meglio descrive la tua qualifica professionale.',
                     width='16em',_class='dlgfield')
                     
        fb.numberTextbox(lbl='!!Posti per pyFiorentina', colspan=3, value = '^.posti_ristorante',
                          tooltip=u"!!Il venerdì sera ci sarà la grandiosa cena pythonica e,<br/>ovviamente, la Fiorentina sarà tenera è gustosa come non mai.<br/>Per poter partecipare segna il numero dei posti desiderati.",
                          width='3em',_class='dlgfield')
        
                               
        fb.checkbox(lbl='!!Studente', value = '^.studente',margin_top='2px', disabled=True)
        
        fb.br()
        fb.horizontalslider(lbl='!!Esperienza', value = '^.py_level',margin_top='2px', 
                            discreteValues='5', width='100px', minimum=0, maximum=4)
        fb.div('^.@@py_level_dsc',style='font-style: italic;font-size: x-small; font-weight: normal;color:#ffe566;',width='130px')
        fb.dataFormula('.@@py_level_dsc','return [l0,l1,l2,l3,l4][lv || 0]',l0=u"!!Nessuna",l1=u"!!Scarsa",l2=u"!!Discreta",
                                         l3=u"!!Buona",l4=u"!!Ottima",lv='^.py_level',_init=True)
        fb.dataScript('.@@py_ristorante_lbl','return "PyFiorentina:" ',_if='posti>0',posti='^.posti_ristorante',_else='return""',_init=True)
        fb.dataScript('.@@py_ristorante_posti','return posti ',_if='posti>0',posti='^.posti_ristorante',_else='return""',_init=True)
        fb.br()
        s = fb.div(lbl='!!Presenza', colspan=3)
        label_style='display:inline; font-style: italic;font-size: x-small; font-weight: normal;color:#ffe566;'
        s.checkbox(u'!!Venerdì',value = '^.presenza_g1',label_style=label_style )
        s.checkbox('!!Sabato', margin_left='10px',value = '^.presenza_g2', label_style=label_style)
        s.checkbox('!!Domenica',margin_left='10px',value = '^.presenza_g3',label_style=label_style)
        
        
      #fb.horizontalslider(lbl='!!Livello', value = '^.py_level',margin_top='2px', 
      #                    discreteValues='5', width='100px', default=2, minimum=0, maximum=4)
      #fb.div('^.py_level')
      #
      #s=tt.div(align='center',colspan=2,margin_top='3px',padding='3px',border_top='1px solid white')
      #label_style='display:inline; font-style: italic;font-size: x-small; font-weight: normal;color:#ffe566;'
      #s.checkbox(u'!!Venerdì',value = '^.presenza_g1',label_style=label_style )
      #s.checkbox('!!Sabato', margin_left='10px',value = '^.presenza_g2', label_style=label_style)
      #s.checkbox('!!Domenica',margin_left='10px',value = '^.presenza_g3',label_style=label_style)
        
    def pageSalva(self, pages):
        client,bottom=self.publicPage(pages,datapath='aux')
        client.div(u"!!Salvataggio in corso...",_class='pbl_largemessage',margin='3em')

    def pageOkSalva(self, pages):
        client,bottom=self.publicPage(pages,datapath='aux')
        client.div(u"!!Le modifiche all'elenco partecipanti sono state salvate",_class='pbl_largemessage',margin='3em')
        bottom.div(u'!!Torna al menù', connect_onclick=self.cancel_url(),_class='pbl_button',float='right')

    def rpc_savePartecipanti(self, partecipanti):
        tblpartecipanti = self.db.table('assopy.partecipante')
        for p in partecipanti.values():
            p.pop('presenze')
            p.pop('tariffa_descrizione')
            
            tblpartecipanti.update(p)
        self.db.commit()
         
            
def index(req, **kwargs):
    return GnrWebPage(req, GnrCustomWebPage, __file__, **kwargs).index()

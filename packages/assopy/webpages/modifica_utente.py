#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  untitled
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#

""" modifica_utente """

from gnr.web.gnrwebpage import GnrWebPage
from gnr.core.gnrbag import Bag

# --------------------------- GnrWebPage subclass ---------------------------
class GnrCustomWebPage(object):
    py_requires='basecomponent:Public'
    def windowTitle(self):
         return '!!Assopy Profilo Utente'
         
    def cancel_url(self):
        return "genro.gotoURL('index.py')"
        
    def pageAuthTags(self, method=None, **kwargs):
        return 'users'

    def main(self, root, **kwargs):
        top, pages = self.publicPagedPane(root, '!!Modifica profilo')
        
        self.pageForm(pages)
        self.pageSaving(pages)
        self.pageSaved(pages)
    
    def pageForm(self,pages):
        cf_check = self.db.table('assopy.anagrafica').js_validate_codiceFiscale()
        piva_check = self.db.table('assopy.anagrafica').js_validate_partitaIva()
        client, bottom = self.publicPage(pages, datapath='form')
        #client.dataRecord('.data.utente', 'assopy.utente', username=self.user, _init=True)
        client.data('.data.utente', self.userRecord())
        #client.dataRecord('.data.anagrafica', 'assopy.anagrafica', utente_id='^.data.utente.id')
        client.data('.data.anagrafica', self.anagraficaRecord())
        client.dataScript('.isValid',"return true", data='=.data',
                                     _if='genro.dataValidate(data)',
                                    _else="genro.focusOnError(data); return false;", dummy='^form.doSave')
        
        client.dataScript('dummy','SET _pbl.selectedPage=1;', isValid='^.isValid', _if='isValid')
        
        client.dataRpc('.response.save','save', data='=.data', _POST=True, isValid='^.isValid' , _if='isValid',
                                 _onResult='SET _pbl.selectedPage=2;')
        client.dataScript('aux.upLocalita','return localita.toUpperCase()', localita='^.data.anagrafica.localita',_if='localita',_init=True)
        
        fb = client.formbuilder(datapath='.data',cols=1, margin_left='2em',border_spacing='7px',margin_top='1em')
        fb.dataScript('dummy',"SET .anagrafica.nazione = 'IT'",_if='localita',localita='^form.sel_loc')
        fb.field('assopy.utente.nome_cognome',width='30em',value='^.utente.nome_cognome',autofocus=True)
        
        fb.field('assopy.utente.email', width='30em', validate_email=True, value='^.utente.email',
                  invalidMessage='!!Indirizzo mail non valido')
        fb.field('assopy.anagrafica.titolo',value='^.anagrafica.titolo',tag='combobox',width='20em',values='!!Sig.,Sig.ra,Dr.,Prof.,Ing.,Spett.')
        fb.field('assopy.anagrafica.ragione_sociale',width='30em',value='^.anagrafica.ragione_sociale',
                  lbl='(*) Ragione sociale',
                     required=True, invalidMessage='!!Obbligatorio')
        
        fb.dbCombobox(lbl=u'!!Località',width='30em',value='^.anagrafica.localita',dbtable='glbl.localita',
                        columns='nome',auxColumns='provincia',selected_nome='^form.sel_loc',
                        selected_cap='^.anagrafica.cap',selected_provincia='^.anagrafica.provincia')
        
        
        fb.dbCombobox(lbl=u'!!Indirizzo',width='30em',value='^.anagrafica.indirizzo',dbtable='glbl.stradario_cap',
                            columns='pref,topo',auxColumns='n_civico,provincia',
                            condition='COMUNE = :loc',condition_loc='=aux.upLocalita',
                            selected_cap='^.anagrafica.cap')

        fb.field('assopy.anagrafica.cap', width='5em',value='^.anagrafica.cap')
        fb.field('assopy.anagrafica.provincia',width='20em',value='^.anagrafica.provincia')
        fb.field('assopy.anagrafica.nazione',width='20em',value='^.anagrafica.nazione')
        fb.field('assopy.anagrafica.cellulare',width='20em',value='^.anagrafica.cellulare')
        fb.field('assopy.anagrafica.codice_fiscale',width='20em',value='^.anagrafica.codice_fiscale',validate_case='u', validate_call=cf_check)
        fb.field('assopy.anagrafica.partita_iva',width='20em',value='^.anagrafica.partita_iva', validate_call=piva_check)
        client.div('!!(*) Indicare il Cognome e Nome se persona fisica.',text_align='left',margin_top='1em',margin_left='1em',_class='pbl_largemessage',font_size='.95em')
        bottom.div('!!Registra', connect_onclick='FIRE form.doSave=true',_class='pbl_button pbl_confirm',float='right')
        bottom.div('!!Annulla',connect_onclick=self.cancel_url(), _class='pbl_button pbl_cancel',float='right')

    def pageSaving(self,pages):
        client,bottom=self.publicPage(pages,datapath='aux')
        client.div(u"!!Salvataggio in corso...", _class='pbl_largemessage', margin_top='1em',margin_right='3em',margin_left='3em')

    def pageSaved(self,pages):
        client,bottom=self.publicPage(pages,datapath='aux')
        client.div(u"!!Profilo salvato",_class='pbl_largemessage',margin='3em')
        bottom.div(u'!!Torna al menù', connect_onclick=self.cancel_url(),_class='pbl_button',float='right')
        
    def rpc_save(self,data=None,**kwargs):
        utente = data['utente']
        utente['locale'] = self.locale
        tbl = self.db.table('assopy.utente')
        tbl.update(utente)
        
        anagrafica = data['anagrafica']
        anagrafica['utente_id'] = utente['id']
        tbl = self.db.table('assopy.anagrafica')
        tbl.insertOrUpdate(anagrafica)
        
        self.db.commit()
        return 'Record Saved'
           
        
def index(req, **kwargs):
    return GnrWebPage(req, GnrCustomWebPage, __file__, **kwargs).index()

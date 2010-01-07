#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  untitled
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#

""" Anagrafica """
import time
import os
from gnr.core.gnrbag import Bag

# --------------------------- GnrWebPage subclass ---------------------------
class GnrCustomWebPage(object):
    maintable='assopy.anagrafica'
    py_requires='public:Public,standard_tables:TableHandler'
    def windowTitle(self):
        return '!!Assopy Anagrafiche'
         
    def pageAuthTags(self, method=None, **kwargs):
        return 'socio'
        
    def tableWriteTags(self):
        return 'admin'
        
    def tableDeleteTags(self):
        return 'superadmin'
        
    def barTitle(self):
        return '!!Gestione Anagrafiche'
        
    def columnsBase(self,):
        return """titolo:4,ragione_sociale:14,@utente_id.username:14,indirizzo:10,
                    localita:10,provincia/Pr.:2,nazione/Naz:3,codice_fiscale/C.Fiscale:11,partita_iva/P.Iva:7"""
               
    def formBase(self,pane,datapath='',disabled=False):
        cf_check = self.db.table('assopy.anagrafica').js_validate_codiceFiscale()
        piva_check = self.db.table('assopy.anagrafica').js_validate_partitaIva()
        
        fb = pane.formbuilder(datapath=datapath,cols=1, margin_left='2em',border_spacing='7px',margin_top='1em',disabled=disabled)
        fb.dataScript('aux.upLocalita','return localita.toUpperCase()', localita='^.localita',_if='localita')
        fb.dataFormula('.nazione',"'I'",_if='localita',localita='^form.sel_loc')
        fb.field('assopy.anagrafica.titolo',value='^.titolo',tag='combobox',width='20em',values='!!Sig.,Sig.ra,Dr.,Prof.,Ing.,Spett.')
        fb.field('assopy.anagrafica.ragione_sociale',width='30em',value='^.ragione_sociale',
                                    lbl='!!Ragione sociale',required=True, invalidMessage='!!Obbligatorio')
        fb.dbCombobox(lbl=u'!!Località',width='30em',value='^.localita',dbtable='glbl.localita',
                            columns='nome',auxColumns='provincia',selected_nome='^form.sel_loc',
                            selected_cap='^.cap',selected_provincia='^.provincia')

        fb.dbCombobox(lbl=u'!!Indirizzo',width='30em',value='^.indirizzo',dbtable='glbl.stradario_cap',
                                columns='pref,topo',auxColumns='n_civico,cap',
                                condition='COMUNE = :comune',condition_comune='=aux.upLocalita',
                                selected_cap='^.cap')
        fb.field('assopy.anagrafica.cap', width='5em',value='^.cap')
        fb.field('assopy.anagrafica.provincia',width='20em',value='^.provincia')
        fb.field('assopy.anagrafica.nazione',width='20em',value='^.nazione')
        fb.field('assopy.anagrafica.cellulare',width='20em',value='^.cellulare')
        fb.field('assopy.anagrafica.codice_fiscale',width='20em',value='^.codice_fiscale',validate_case='u', validate_call=cf_check)
        fb.field('assopy.anagrafica.partita_iva',width='20em',value='^.partita_iva', validate_call=piva_check)
        
        fb.field('assopy.anagrafica.tipo_iva',width='20em',value='^.tipo_iva')
        fb.field('assopy.anagrafica.tipo_cliente',width='20em',value='^.tipo_cliente')
        
    def orderBase(self):
        return 'ragione_sociale'
    
    def queryBase(self):
        return dict(column='ragione_sociale',op='contains', val=None)
                               
def index(req, **kwargs):
    return GnrWebPage(req, GnrCustomWebPage, __file__, **kwargs).index()
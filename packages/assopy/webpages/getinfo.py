#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  untitled
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#

""" info """
import os

# --------------------------- GnrWebPage subclass ---------------------------
class GnrCustomWebPage(object):
    def main(self, root, **kwargs):
        root.h1('Url invalido')

def _page(req):
    return GnrWebPage(req, GnrCustomWebPage, __file__)

def riepilogo(req):
    righe= _page(req).db.table('assopy.ordine_riga').query('@tariffa_id.descrizione as tariffa ,count(*) as numero,sum(t0.importo) as importo',
                                                    group_by='@tariffa_id.descrizione',
                                                    where='@ordine_id.fattura_num is not null').selection().output('dictlist')
    return righe

def riepilogo_in_attesa(req):
    righe= _page(req).db.table('assopy.ordine_riga').query('@tariffa_id.descrizione as tariffa ,count(*) as numero,sum(t0.importo) as importo',
                                                        group_by='@tariffa_id.descrizione',
                                                        where='@ordine_id.fattura_num is null AND @ordine_id.data_pagamento is null').selection().output('dictlist')
    return righe
    
def classifica_url(req,**kwargs):
    page = GnrWebPage(req, GnrCustomWebPage, __file__, **kwargs)
    tplfile = page.getResource(os.path.join('doc_templates', 'classifica.tpl'))
    return page.index(mako=tplfile)  
    
def classifica(req,**kwargs):
    page = GnrWebPage(req, GnrCustomWebPage, __file__, **kwargs)
    tplfile = page.getResource(os.path.join('doc_templates', 'classifica.tpl'))
    return page.index(mako=tplfile) 

def classifica_normalizzata(req,**kwargs):
    page = GnrWebPage(req, GnrCustomWebPage, __file__, **kwargs)
    tplfile = page.getResource(os.path.join('doc_templates', 'classifica_normalizzata.tpl'))
    return page.index(mako=tplfile)
    
def partecipanti(req):
    return _page(req).db.table('assopy.partecipante').query(where="$cognome >'' and $nome >''").count()
    
def badge(req, order='c'):
    order = order.lower()
    if order == 'c':
        order = '$ragione_sociale, $cognome'
    if order == 'a':
        order = '$cognome'
    if order == 'n':
        order = '$ordine_numero'
    partecipanti = _page(req).db.query('assopy.partecipante', 
                    columns="""$nome, $cognome, $qualifica_badge, $presenza, $py_level, $tariffa_tipo, $studente,
                               $posti_ristorante, $ordine_numero, $numero_riga, $fattura_num, $ragione_sociale,
                               $username, $email
                            """,
                    where='@ordine_riga_id.@ordine_id.data_conferma IS NOT NULL', 
                    relationDict={'ordine_numero':'@ordine.numero', 'numero_riga':'@ordine_riga_id.numero_riga',
                                  'fattura_num':'@ordine.fattura_num', 'ragione_sociale':'@ordine.@anagrafica_id.ragione_sociale',
                                   'username':'@utente.username', 'email':'@utente.email'},
                    order_by=order
                    ).selection()
    return partecipanti.output('tabtext')

def partecipanti_fatturati(req):
    return _page(req).db.table('assopy.partecipante').query(where="$cognome >'' and $nome >'' and $fattura>''").count()

def lista_partecipanti_bozze(req):
    return _page(req).db.table('assopy.partecipante').query(where="$cognome >'' and $nome >'' and $fattura>''").count()


def partecipanti_confermati(req):
    return _page(req).db.table('assopy.partecipante').query(where="$cognome >'' and $nome >'' and @ordine.data_conferma is not null").count()
                   
def partecipanti_totale(req):
    return _page(req).db.table('assopy.partecipante').query().count()
        
def ordini(req):
    return 'Ordini: %s' % _page(req).db.table('assopy.ordine').query().count()

def talk(req,id=None,columns=None):
    if not columns:
        columns= """$id,$codice,$durata,$titolo,$abstract,$abstract_en,$lingua,$sala,$data,$ora_inizio,$ora_fine,$oratore2_id,
                    @track_id.codice as track,
                    @oratore_id.attivita as attivita,
                    @oratore_id.settore as settore,
                    @oratore_id.www as www,
                    @oratore_id.@anagrafica_id.ragione_sociale as ragione_sociale ,
                    @oratore_id.@anagrafica_id.indirizzo as indirizzo,
                    @oratore_id.@anagrafica_id.localita as localita,                                                               
                    @oratore_id.@anagrafica_id.provincia as provincia,
                    @oratore_id.@anagrafica_id.cap as cap, 
                    @oratore_id.@anagrafica_id.nazione as nazione , 
                    @oratore_id.@anagrafica_id.cellulare as cellulare ,
                    @oratore_id.@anagrafica_id.@utente_id.username as username,
                    @oratore_id.@anagrafica_id.@utente_id.nome_cognome as nome ,
                    @oratore_id.@anagrafica_id.@utente_id.email as email, 
                    @oratore2_id.@anagrafica_id.@utente_id.nome_cognome as oratore2_nome
                    """
    if id:
        query= _page(req).db.table('assopy.talk').query(where='$id=:id',id=id,columns=columns)
    else:
        query= _page(req).db.table('assopy.talk').query(columns=columns)
    return query.selection().output('dictlist')

def speaker(req,username=None,columns=None):
    if not columns:
        columns= """$id,$attivita,$settore,$www,$presentazione,$presentazione_en,
                    @anagrafica_id.ragione_sociale as ragione_sociale,
                    @anagrafica_id.indirizzo as indirizzo,
                    @anagrafica_id.localita as localita,                                                               
                    @anagrafica_id.provincia as provincia,
                    @anagrafica_id.cap as cap, 
                    @anagrafica_id.nazione as nazione , 
                    @anagrafica_id.cellulare as cellulare ,
                    @anagrafica_id.@utente_id.username as username,
                    @anagrafica_id.@utente_id.nome_cognome as nome ,
                    @anagrafica_id.@utente_id.email as email"""
    if username:
        query= _page(req).db.table('assopy.oratore').query(where='@anagrafica_id.@utente_id.username=:username',username=username,columns=columns)
    else:
        query= _page(req).db.table('assopy.oratore').query(columns=columns)
    return query.selection().output('dictlist')
    
def utenti(req):
    return 'Utenti: %s' % _page(req).db.table('assopy.utente').query(where='stato=:st',st='confermato').count()
def index(req, **kwargs):
    return GnrWebPage(req, GnrCustomWebPage, __file__, **kwargs).index()


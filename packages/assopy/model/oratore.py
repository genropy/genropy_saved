#!/usr/bin/env python
# encoding: utf-8

class Table(object):

    def config_db(self, pkg):
        tbl =  pkg.table('oratore',  pkey='id',name_long='!!Oratore', name_plural='!!Oratori', rowcaption='nome_cognome')
        tbl.column('id',size='22',group='_',readOnly='y',name_long='Id')
        tbl.column('anagrafica_id', size='22',name_long='Id anagrafica').relation('assopy.anagrafica.id', one_one=True, mode='foreignkey')
        tbl.column('attivita', size=':25',name_long=u'!!Attività')
        tbl.column('settore', size=':25',name_long=u'!!Settore')
        tbl.column('presentazione',name_long='!!Presentazione')
        tbl.column('presentazione_en',name_long='!!Presentazione Inglese')
        tbl.column('www', size=':40',name_long='!!Homepage')
        
        tbl.aliasColumn('email', relation_path='@anagrafica_id.@utente_id.email', name_long='!!Email')
        tbl.aliasColumn('nome_cognome', relation_path='@anagrafica_id.@utente_id.nome_cognome', name_long='!!Nome e Cognome')
        tbl.aliasTable('utente', relation_path='@anagrafica_id.@utente_id', name_long='!!Utente')
        

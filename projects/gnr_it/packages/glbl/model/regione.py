#!/usr/bin/env python
# encoding: utf-8

class Table(object):
    def config_db(self, pkg):
        tbl = pkg.table('regione', pkey='sigla', 
        	name_long='!!Regione', rowcaption='sigla,nome',caption_field='nome',lookup=True)
        tbl.column('sigla', size='3', group='_', readOnly=True, name_long='!!Sigla', indexed=True)
        tbl.column('nome', name_long='!!Nome', indexed=True)
        tbl.column('nome_locale', name_long='!!Nome Locale', indexed=True)
        tbl.column('codice', 'I', name_long='!!Codice')
        tbl.column('codice_istat', size='2', name_long='!!Codice Istat')
        tbl.column('ordine', size='6', name_long='!!Ordine Gnr')
        tbl.column('zona', name_long='!!Zona')
        tbl.column('zona_numero', 'I', name_long='!!Zona n.')
        tbl.column('nuts',name_long='!!NUTS2').relation('glbl.nuts.code',relation_name='regioni',onDelete='raise')



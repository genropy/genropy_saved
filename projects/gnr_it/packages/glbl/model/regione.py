#!/usr/bin/env python
# encoding: utf-8

class Table(object):
    def config_db(self, pkg):
        tbl = pkg.table('regione', pkey='sigla', 
        	name_long='!![it]Regione', rowcaption='sigla,nome',caption_field='nome',lookup=True)
        tbl.column('sigla', size='3', group='_', readOnly=True, name_long='!![it]Sigla', indexed=True)
        tbl.column('nome', size=':128', name_long='!![it]Nome', indexed=True)
        tbl.column('nome_locale', size=':128', name_long='!![it]Nome Locale', indexed=True)
        tbl.column('codice', 'I', name_long='!![it]Codice')
        tbl.column('codice_istat', size='2', name_long='!![it]Codice Istat')
        tbl.column('ordine', size='6', name_long='!![it]Ordine Gnr')
        tbl.column('zona', name_long='!![it]Zona')
        tbl.column('zona_numero', 'I', name_long='!![it]Zona n.')
        tbl.column('nuts', size=':128', name_long='!![it]NUTS2').relation('glbl.nuts.code',relation_name='regioni')



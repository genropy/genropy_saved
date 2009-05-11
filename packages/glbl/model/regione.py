#!/usr/bin/env python
# encoding: utf-8

class Table(object):
   
    def config_db(self, pkg):
        
        tbl =  pkg.table('regione',  pkey='sigla',name_long='Regione', rowcaption='sigla,nome')
        tbl.column('sigla',size='3',group='_',readOnly='y',name_long='Sigla', indexed='y')
        tbl.column('nome',size=':22',name_long='Nome', indexed='y')
        tbl.column('codice_istat',size='2',name_long='Codice Istat')
        tbl.column('ordine',size='6',name_long='Ordine Gnr')
        tbl.column('zona',size='6',name_long='Zona')



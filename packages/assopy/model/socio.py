#!/usr/bin/env python
# encoding: utf-8

class Table(object):

    def config_db(self, pkg):
        tbl =  pkg.table('socio',  pkey='id',name_long='Socio',name_plural='!!Soci', rowcaption='nome_cognome')
        tbl.column('id',size='22',group='_',readOnly='y',name_long='Id')
        tbl.column('nome_cognome', size=':32',name_long='Nome e cognome')
        tbl.column('data_inizio', 'D' ,name_long='Data di associazione')
        tbl.column('data_fine', 'D' ,name_long='Data di fine associazione')
        tbl.column('anagrafica_id', size='22',name_long='Id anagrafica').relation('assopy.anagrafica.id', one_one=True, mode='foreignkey')
        tbl.column('www', size=':40',name_long='Homepage')
        tbl.column('attivita', size=':25',name_long=u'Attività')
        tbl.column('settore', size=':25',name_long='Settore')
        tbl.column('descrizione',name_long='Descrizione')
        tbl.table_alias('valutazione', relation_path='@anagrafica_id.@utente_id.@assopy_valutazione_utente_id', name_long='Valutazioni')

#!/usr/bin/env python
# encoding: utf-8

class Table(object):

    def config_db(self, pkg):
        tbl =  pkg.table('evento',  pkey='id',name_long='!!Evento', name_plural='!!Eventi',
                       rowcaption='codice,edizione,titolo:(%s-%s) %s')
        tbl.column('id',size='22',group='_',readOnly='y',name_long='Id')
        tbl.column('codice', size=':12', name_long='!!Codice')
        tbl.column('data_inizio', 'D', name_long='!!Data inizio')
        tbl.column('data_fine', 'D', name_long='!!Data fine')
        tbl.column('titolo', size=':21',name_long='!!Titolo')
        tbl.column('descrizione',name_long='!!Descrizione')
        tbl.column('edizione','L', name_long='!!Edizione')
        tbl.column('location', size=':24', name_long='!!Location')
        tbl.column('indirizzo',name_long='!!Indirizzo')        
        tbl.column('localita', size=':40',name_long=u'!!Località')
        tbl.column('provincia', size=':3',name_long='!!Provincia').relation('glbl.provincia.sigla')
        tbl.column('cap', size=':5',name_long='!!CAP')
        tbl.column('homepage', size=':31',name_long='Homepage')
        tbl.column('scadenza_importo_1', 'D', name_long='Scadenza Importo 1')
        tbl.column('scadenza_importo_2', 'D', name_long='Scadenza Importo 2')

#!/usr/bin/env python
# encoding: utf-8

class Table(object):

    def config_db(self, pkg):
        tbl =  pkg.table('talk', pkey='id', name_long='!!Talk', name_plural='!!Talks',
                                rowcaption='@oratore_id.nome_cognome,titolo:%s - %s')
        tbl.column('id', size='22', group='_', readOnly='y', name_long='!!Id')
        tbl.column('codice', size=':12',name_long='!!Codice')
        tbl.column('oratore_id', size='22', group='_', name_long='Id Oratore').relation('assopy.oratore.id', mode='foreignkey',
                                                                                             one_name='!!Oratore',  many_name='!!Talks')
        tbl.column('durata', 'L', name_long='!!Durata')
        tbl.column('titolo', size=':50',name_long='!!Titolo')
        tbl.column('argomento',size=':50',name_long='!!Argomento')
        tbl.column('abstract',name_long='!!Abstract')
        tbl.column('abstract_en',name_long='!!English Abstract')
        tbl.column('track_id', size='22', group='_', name_long='Track Id').relation('assopy.track.id', mode='foreignkey',
                                                                                     one_name='!!Track',  many_name='!!Talks') # codice?
        tbl.column('evento_id', size='22', group='_', name_long='!!Evento').relation('assopy.evento.id', mode='foreignkey',
                                                                                     one_name='!!Evento',  many_name='!!Talks')
        tbl.column('lingua',size=':10', name_long='!!Lingua')
        tbl.column('sala', size=':10', name_long='!!Sala')
        tbl.column('data', 'D', name_long='!!Data')
        tbl.column('ora_inizio', 'H', name_long='!!Ora Inizio')
        tbl.column('ora_fine', 'H', name_long='!!Ora Fine')
        tbl.column('oratore2_id', size='22',name_long='!!Oratore2_ID').relation('assopy.oratore.id',  one_name='!!Secondo oratore',  many_name='!!Talks secondo')
        tbl.aliasColumn('voto', relation_path='@assopy_valutazione_talk_id.voto', name_long='!!Voto')
    
        
        
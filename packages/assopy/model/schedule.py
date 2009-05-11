#!/usr/bin/env python
# encoding: utf-8
from gnr.core.gnrbag import Bag

class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('schedule',  pkey='id',name_long='!!Schedule',name_plural='!!Schedule',rowcaption='data,luogo,ora_inizio,ora_fine')
        tbl.column('id',size='22',group='_',readOnly='y',name_long='Id')
        tbl.column('nome', name_long='!!Nome')
        tbl.column('descrizione', name_long='!!Descrizione')
        tbl.column('luogo', size=':10', name_long='!!Luogo')
        tbl.column('data', 'D', name_long='!!Data')
        tbl.column('ora_inizio', 'H', name_long='!!Ora inizio')
        tbl.column('ora_fine', 'H', name_long='!!Ora fine')
        tbl.column('durata', 'L', name_long='!!Durata')
        tbl.column('talk_id', size='22', name_long='!!Talk').relation('assopy.talk.id')
        
        
        
        
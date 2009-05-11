#!/usr/bin/env python
# encoding: utf-8

class Table(object):
   
    def config_db(self, pkg):
        
        tbl =  pkg.table('iscrizione_evento',  pkey='id',name_long='Iscrizione evento', rowcaption='nome,cognome,@evento_id.codice: %s %s-%s')
        tbl.column('id',size='22',group='_',readOnly='y',name_long='Id')
        tbl.column('nome_cognome', size=':32',name_long='Nome e cognome')
        tbl.column('email', size=':25',name_long='Email')
        tbl.column('data_iscrizione', 'D' ,name_long='Data iscrizione')
        tbl.column('data_nascita', 'D' ,name_long='Data di nascita')
        tbl.column('ordine_riga_id', size='22',name_long='Riga ordine').relation('assopy.ordine_riga.id', one_one=True)
        tbl.column('anagrafica_id', size='22',name_long='Id anagrafica').relation('assopy.anagrafica.id', one_one=True)




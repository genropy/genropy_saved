#!/usr/bin/env python
# encoding: utf-8

class Table(object):
#id, id_tariffa, id_evento, descrizione
    def config_db(self, pkg):
        tbl =  pkg.table('sponsorizzazione',
                          pkey='id',
                          name_long='Sponsorizzazione',
                          name_plural='!!Sponsorizzazioni',
                          rowcaption='sponsor,@evento_id.codice,@tariffa_id.codice')
                          
        tbl.column('id',size='22',group='_',readOnly='y',name_long='Id')
        
        tbl.column('sponsor', size=':25',name_long='Sponsor')
        tbl.column('descrizione',name_long='Descrizione')
        tbl.column('www', size=':40',name_long='Homepage')
        tbl.column('attivita', size=':25',name_long=u'Attività')
        tbl.column('settore', size=':25',name_long=u'Settore')
        tbl.column('logo',size=':30', name_long='Logo')
        
        tbl.column('evento_id', size='22',name_long='Evento').relation('assopy.evento.id', mode='foreignkey')
        tbl.column('ordine_riga_id', size='22',name_long='Riga ordine').relation('assopy.ordine_riga.id', one_one=True, mode='foreignkey')
        tbl.column('anagrafica_id', size='22',name_long='Id anagrafica').relation('assopy.anagrafica.id', one_one=True, mode='foreignkey')




        

        

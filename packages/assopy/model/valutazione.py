#!/usr/bin/env python
# encoding: utf-8
"""
valutazione.py

Created by Saverio Porcari on 2008-01-31.

"""

class Table(object):
   
    def config_db(self, pkg):
        
        tbl =  pkg.table('valutazione',  pkey='id',name_long='Valutazione',name_plural='!!Valutazioni', rowcaption='@utente_id.nome_cognome,@talk_id.titolo,voto')
        tbl.column('id',size='22',group='_',readOnly='y',name_long='Id')
        tbl.column('talk_id', size='22',name_long='Evento').relation('assopy.talk.id', mode='foreignkey')
        tbl.column('utente_id', size='22',name_long='Utente').relation('assopy.utente.id', mode='foreignkey')
        tbl.column('voto','L',name_long='Voto')
        tbl.column('note',name_long='Note')
        

    def creaClassifica(self):
        columns="""@talk_id.@oratore_id.@anagrafica_id.@utente_id.nome_cognome as speaker,
                   @talk_id.titolo as talk,
                   @talk_id.durata as durata,
                   @talk_id.@track_id.titolo as track,
                   @talk_id.@track_id.codice as track_code,
                   @utente_id.nome_cognome as socio,
                   $utente_id,
                   $talk_id,
                   $voto,
                   $note"""
        sel=self.query(columns=columns,where='$voto > 0').selection()
        sel.totalize(group_by=['*per_talk','talk_id'],sum=['voto'],keep=['speaker','talk','track','track_code','durata'],collect=['voto'])
        sel.totalize(group_by=['*per_track','track','talk_id'],sum=['voto'],keep=['speaker','talk','track','track_code','durata'],collect=['voto'])
        totalizer=sel.totalizer()
        for n in totalizer['per_talk']:
            n.attr['media']=round(n.attr['sum_voto']*1./len(n.attr['collect_voto']),2)
        for v in totalizer['per_track'].values():
            for n in v:
                n.attr['media']=n.attr['sum_voto']*1./len(n.attr['collect_voto'])
        return sel
    
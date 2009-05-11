#!/usr/bin/env python
# encoding: utf-8

class Table(object):

    def config_db(self, pkg):
        tbl =  pkg.table('partecipante',  pkey='id',name_long='!!Partecipante',name_plural='!!Partecipanti',
        rowcaption='cognome,nome,azienda')
        
        tbl.column('id',size='22',group='_',readOnly='y',name_long='Id')
        
        tbl.column('ordine_riga_id',size='22',group='_').relation('assopy.ordine_riga.id', 
                                                              one_name='!!Riga ordine',  many_name='!!Partecipante',
                                                             one_one=True, mode='foreignkey')
        tbl.column('cognome', size=':60',name_long='!!Cognome')
        tbl.column('nome', size=':60',name_long='!!Nome')
        tbl.column('azienda', size=':60',name_long='!!Azienda')
        tbl.column('studente', 'B', name_long='!!Studente')
        tbl.column('presenza_g1', 'B', name_long='!!Giorno 1')
        tbl.column('presenza_g2', 'B', name_long='!!Giorno 2')
        tbl.column('presenza_g3', 'B', name_long='!!Giorno 3')
        tbl.column('py_level', size=':1', name_long='!!Conoscenza Python')
        tbl.column('tariffa_tipo', size=':12', name_long='!!Tipo tariffa')
        tbl.column('qualifica_badge', name_long='!!Qualifica sul badge')
        tbl.column('posti_ristorante', 'L',name_long='!!Posti PyFiorentina')
        tbl.aliasTable('ordine', relation_path='@ordine_riga_id.@ordine_id',name_long='Ordine')
        tbl.aliasTable('cliente', relation_path='@ordine.@anagrafica_id',name_long='Cliente')
        tbl.aliasTable('utente', relation_path='@cliente.@utente_id',name_long='Utente')
        tbl.aliasColumn('fattura', relation_path='@ordine.fattura_num',name_long='!!Fattura')
        tbl.aliasColumn('data_conferma', relation_path='@ordine.data_conferma',name_long='!!Data conferma')
        tbl.formulaColumn('fullname',"(nome||' '|| cognome)",name_long='!!Partecipante')
        tbl.formulaColumn('presenza',"(repeat('Ven',cast($presenza_g1 as int)) || '-' || repeat('Sab',cast($presenza_g2 as int)) || '-' || repeat('Dom',cast($presenza_g3 as int)))",name_long='!!G.Presenza')
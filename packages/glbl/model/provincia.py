#!/usr/bin/env python
# encoding: utf-8

class Table(object):
    def config_db(self, pkg):
        tbl = pkg.table('provincia', pkey='sigla', name_long='Provincia',
                        rowcaption='$nome,$sigla:%s (%s)')
        tbl.column('sigla', size='2', group='_', readOnly='y', name_long='Sigla', indexed='y')
        tbl.column('regione', size='3', name_long='Regione').relation('glbl.regione.sigla')
        tbl.column('nome', size=':30', name_long='Nome', indexed='y')
        tbl.column('codice_istat', size='3', name_long='Codice Istat')
        tbl.column('ordine', 'L', name_long='Ordine Gnr')
        tbl.column('ordine_tot', size='6', name_long='Ordine tot Gnr')
        tbl.column('cap_valido', size='2', name_long='CAP Valido')

        
    def baseView_cap(self):
        return "nome,cap_valido"
        
    
    def baseView_regione(self):
        return "nome:60%,@regione.nome/Regione:40%"
    
    def baseView_full(self):
        return "sigla:10%,@regione.nome/Regione:40%,nome:20%,@regione.zona:30%"




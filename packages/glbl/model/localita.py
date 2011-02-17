#!/usr/bin/env python
# encoding: utf-8

class Table(object):
    def config_db(self, pkg):
        tbl = pkg.table('localita', pkey='id', name_long='Localita', rowcaption='nome,@provincia.sigla:%s (%s)')
        tbl.column('id', size='22', group='_', readOnly='y', name_long='Id')
        tbl.column('nome', size=':52', name_long='Nome', indexed='y')
        tbl.column('provincia', size='2', name_long='Provincia').relation('glbl.provincia.sigla', mode='foreignkey',
                                                                          onUpdate_sql='cascade', onDelete='raise')
        tbl.column('codice_istat', size='6', name_long='Codice Istat')
        tbl.column('codice_comune', size='4', name_long='Codice Comune')
        tbl.column('prefisso_tel', size='4', name_long='Prefisso Tel')
        tbl.column('cap', size='5', name_long='CAP', indexed='y')
    
    def baseView_min(self):
        return "nome:80%,prefisso_tel:20%"



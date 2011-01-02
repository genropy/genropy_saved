#!/usr/bin/env python
# encoding: utf-8

class Table(object):
    def config_db(self, pkg):
        tbl = pkg.table('stradario_cap', pkey='id', name_long='Stradario Cap', rowcaption='pref,topo')

        tbl.column('id', size='22', group='_', readOnly='y', name_long='Id')
        tbl.column('cap', size=':8', name_long='CAP')
        tbl.column('provincia', size='2', name_long='Provincia').relation('glbl.regione.sigla')
        tbl.column('comune', size=':42', name_long='Comune')
        tbl.column('comune2', size=':42', name_long='Comune 2')
        tbl.column('frazione', size=':42', name_long='Frazione')
        tbl.column('frazione2', size=':42', name_long='Frazione 2')
        tbl.column('topo', size=':62', name_long='Topo')
        tbl.column('topo2', size=':62', name_long='Topo 2')
        tbl.column('pref', name_long='Pref')
        tbl.column('n_civico', name_long='n_civico')

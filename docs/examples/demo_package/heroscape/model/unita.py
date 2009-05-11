#!/usr/bin/env python
# encoding: utf-8
"""
agente.py

Created by Saverio Porcari on 2008-02-29.
Copyright (c) 2008 __MyCompanyName__. All rights reserved.
"""

class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('unita',  pkey='id',name_long='Unita', rowcaption='nome', group_combo='Combo')
        tbl.column('id',size='22',group='_',readOnly='y',name_long='Id')
        tbl.column('nome', size=':42',name_long='Nome', indexed='y')
        tbl.column('mondo', size=':15',name_long='Mondo', indexed='y')
        tbl.column('tipo_id',size='22',name_long=u'Tipo unita Id', group='_').relation('heroscape.tipo.id', one_group='*')
        tbl.column('numero_miniature', dtype='L', name_long='Numero miniature')
        tbl.column('altezza', dtype='L', name_long='Altezza')
        tbl.column('dimensione', size=':2', name_long='Dimensione')
        tbl.column('generale_id',size='22',name_long='Generale Id', group='_').relation('heroscape.generale.id', one_name='generale', one_group='*')
        tbl.column('razza_id',size='22',name_long='Razza Id', group='_').relation('heroscape.razza.id', one_group='*')
        tbl.column('personalita_id',size='22',name_long=u'Personalita Id', group='_').relation('heroscape.personalita.id', one_group='*')
        tbl.column('classe_id',size='22',name_long=u'Classe Id', group='_').relation('heroscape.classe.id', one_group='*')
        tbl.column('prodotto_id',size='22',name_long='Prodotto Id', group='_').relation('heroscape.prodotto.id', one_group='*')
        tbl.column('movimento', dtype='L', name_long='Movimento')
        tbl.column('vite', dtype='L', name_long='Vite')
        tbl.column('attacco', dtype='L', name_long='Attacco')
        tbl.column('gittata', dtype='L', name_long='Gittata')
        tbl.column('difesa', dtype='L', name_long='Difesa')
        tbl.column('costo_punti', dtype='L', name_long='Costo punti')
        
        tbl.aliasColumn('razza', '@razza_id.nome', name_long='Razza')
        tbl.aliasColumn('generale', '@generale_id.nome', name_long='Generale')
        tbl.aliasColumn('personalita', '@personalita_id.nome', name_long=u'Personalità')
        tbl.aliasColumn('classe', '@classe_id.nome', name_long='Classe')
        tbl.aliasColumn('prodotto', '@prodotto_id.nome', name_long='Nome prodotto')
        tbl.aliasColumn('tipo', '@tipo_id.nome', name_long=u'Tipo unità')
        tbl.aliasColumn('abilita',
                        '@heroscape_abilita_unita_id.nome',
                        name_long=u'!!Abilità')
                        
        tbl.aliasTable('combo',
                        '@heroscape_combo_unita_unita_id.@combo_id',
                        name_long='!!Combo')
        tbl.aliasTable('eserciti',
                        '@heroscape_appartenenza_esercito_unita_id.@esercito_id',
                        name_long='!!Eserciti')
        

        


#!/usr/bin/env python
# encoding: utf-8

class Table(object):
    def config_db(self, pkg):
        tbl = pkg.table('provincia', pkey='sigla', name_long='Provincia',
                         rowcaption='$nome,$sigla:%s (%s)')
        tbl.column('sigla', size='2', readOnly=True, name_long='!!Sigla', indexed=True,validate_notnull=True,
                    validate_len='2',validate_case='u')
        tbl.column('regione', size='3', name_long='!!Regione',validate_notnull=True).relation('glbl.regione.sigla',
                                                                        relation_name='province',
                                                                        eager_one=True)
        tbl.column('nome', size=':30', name_long='!!Nome', indexed=True,validate_notnull=True)
        tbl.column('codice_istat', size='3', name_long='!!Codice Istat',validate_notnull=True)
        tbl.column('ordine', 'L', name_long='!!Ordine Gnr')
        tbl.column('ordine_tot', size='6', name_long='!!Ordine tot Gnr')
        tbl.column('cap_valido', size='2', name_long='!!CAP Valido')
        tbl.column('auxdata','X',name_long='!!test')
        
        
        tbl.column('dimensione',name_long='!!Dimensione',values='P:Piccola,M:Media,G:Grande')
        
        tbl.aliasColumn('regione_nome',relation_path='@regione.nome',name_long='Region nome')

    def baseView_cap(self):
        return "nome,cap_valido"
        
    def baseView_regione(self):
        return "nome:60%,@regione.nome/Regione:40%"
        
    def baseView_full(self):
        return "sigla:10%,@regione.nome/Regione:40%,nome:20%,@regione.zona:30%"

    #def protect_update(self, record, old_record=None):
    #    if record['sigla'] == 'AO':
    #        record.setAttr('regione',wdg_disabled=True,wdg_color='red')
        
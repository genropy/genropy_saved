#!/usr/bin/env python
# encoding: utf-8

class Table(object):
    def config_db(self, pkg):
        tbl = pkg.table('regione')
        tbl.column('province_principali_sigla' ,name_long='!!Prov principali',
                  caption_field='province_principali_nome')
        tbl.formulaColumn('province_principali_nome',"array_to_string(ARRAY(#prov_nomi),',')",
                            select_prov_nomi=dict(table='glbl.provincia',columns='$nome',
                            where="$sigla = ANY(string_to_array(#THIS.province_principali_sigla,','))",order_by='$nome'),
                            )

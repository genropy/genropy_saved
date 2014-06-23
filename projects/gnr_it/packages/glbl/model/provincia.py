#!/usr/bin/env python
# encoding: utf-8

class Table(object):
    def config_db(self, pkg):
        tbl = pkg.table('provincia', pkey='sigla', name_long='Provincia',
                         rowcaption='$nome,$sigla:%s (%s)',caption_field='nome',lookup=True)
        tbl.column('sigla', size='2', readOnly=True, name_long='!!Sigla', indexed=True,validate_notnull=True,
                    validate_len='2',validate_case='u')
        tbl.column('regione', size='3', name_long='!!Regione',validate_notnull=True).relation('glbl.regione.sigla',
                                                                        relation_name='province',
                                                                        eager_one=True)
        tbl.column('nome', name_long='!!Nome', indexed=True,validate_notnull=True)
        tbl.column('nome_locale', name_long='!!Nome Locale', indexed=True)
        tbl.column('codice', name_long='!!codice', dtype='I')
        tbl.column('codice_istat', size='3', name_long='!!Codice Istat',cell_edit=True)
        tbl.column('ordine', 'L', name_long='!!Ordine Gnr')
        tbl.column('ordine_tot', size='6', name_long='!!Ordine tot Gnr')
        tbl.column('cap_valido', size='2', name_long='!!CAP Valido')
            
        tbl.column('nuts',name_long='!!NUTS3').relation('glbl.nuts.code',relation_name='province',onDelete='raise')




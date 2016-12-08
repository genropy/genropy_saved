#!/usr/bin/env python
# encoding: utf-8

class Table(object):
    def config_db(self, pkg):
        tbl = pkg.table('provincia', pkey='sigla', name_long='Provincia',
                         rowcaption='$nome,$sigla:%s (%s)',caption_field='sigla',lookup=True)
        tbl.column('sigla', size='2', readOnly=True, name_long='!![it]Sigla', indexed=True,validate_notnull=True,
                    validate_len='2',validate_case='u')
        tbl.column('regione', size='3', name_long='!![it]Regione',validate_notnull=True).relation('glbl.regione.sigla',
                                                                        relation_name='province',
                                                                        eager_one=True)
        tbl.column('nome', size=':128', name_long='!![it]Nome', indexed=True,validate_notnull=True)
        tbl.column('nome_locale', size=':128'   , name_long='!![it]Nome Locale', indexed=True)
        tbl.column('codice', name_long='!![it]codice', dtype='I')
        tbl.column('codice_istat', size='3', name_long='!![it]Codice Istat')
        tbl.column('ordine', 'L', name_long='!![it]Ordine Gnr')
        tbl.column('ordine_tot', size='6', name_long='!![it]Ordine tot Gnr')
        tbl.column('cap_valido', size='2', name_long='!![it]CAP Valido')
            
        tbl.column('nuts', size=':128' ,name_long='!![it]NUTS3').relation('glbl.nuts.code',relation_name='province')


        tbl.aliasColumn('zona_regione',relation_path='@regione.zona',name_long='Zona Reg')


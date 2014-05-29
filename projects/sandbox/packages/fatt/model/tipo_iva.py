#!/usr/bin/env python
# encoding: utf-8

class Table(object):
    def config_db(self, pkg):
        tbl = pkg.table('tipo_iva', pkey='codice', name_long='!!Tipo iva', 
                        name_plural='!!Tipi iva',caption_field='descrizione',lookup=True)
        self.sysFields(tbl,id=False)
        tbl.column('codice' ,size=':5',name_long='!!Codice')
        tbl.column('descrizione',name_long='!!Descrizione')
        tbl.column('aliquota',dtype='percent',name_long='!!Aliquota')
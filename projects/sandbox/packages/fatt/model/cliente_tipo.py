#!/usr/bin/env python
# encoding: utf-8

class Table(object):
    def config_db(self, pkg):
        tbl = pkg.table('cliente_tipo', pkey='codice', name_long='!!Cliente tipo', 
                        name_plural='!!Cliente tipi',caption_field='descrizione',lookup=True)
        self.sysFields(tbl,id=False)
        tbl.column('codice' ,size=':5',name_long='!!Codice')
        tbl.column('descrizione',name_long='!!Descrizione')
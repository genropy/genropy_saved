#!/usr/bin/env python
# encoding: utf-8

class Table(object):
    def config_db(self, pkg):
        tbl = pkg.table('pagamento_tipo', pkey='codice', name_long='!!Pagamento tipo', 
                        name_plural='!!Pagamento tipi',caption_field='descrizione',lookup=True)
        self.sysFields(tbl,id=False)
        tbl.column('codice' ,size=':5',name_long='!!Codice')
        tbl.column('descrizione',name_long='!!Descrizione')
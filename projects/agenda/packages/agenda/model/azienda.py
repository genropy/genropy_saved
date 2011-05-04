# encoding: utf-8

class Table(object):
    def config_db(self, pkg):
        tbl = pkg.table('azienda', pkey='id', rowcaption='@anagrafica_id.ragione_sociale',
                         name_long='!!Azienda', name_plural='!!Aziende')
        self.sysFields(tbl)
        tbl.column('anagrafica_id',size=':22',name_long='!!Anagrafica id',group='_').relation('sw_base.anagrafica.id', mode='foreignkey')
        tbl.column('tipologia',size=':22',name_long='!!Tipologia')
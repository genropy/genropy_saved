# encoding: utf-8

class Table(object):
    def config_db(self, pkg):
        tbl = pkg.table('azienda', pkey='id', rowcaption='@anagrafica_id.ragione_sociale',
                         name_long='!!Company', name_plural='!!Companies')
        self.sysFields(tbl)
        tbl.column('anagrafica_id',size=':22',name_long='!!Registry id').relation('sw_base.anagrafica.id', mode='foreignkey')
        tbl.column('tipologia',size=':22',name_long='!!Type')
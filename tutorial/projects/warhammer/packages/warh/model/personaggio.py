# encoding: utf-8

class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('personaggio',pkey='id',name_long='!!Personaggio',
                      name_plural='!!Personaggi')
        self.sysFields(tbl)
        tbl.column('nome',name_long='!!Nome')
        tbl.column('sigla',name_long='!!Sigla')
        tbl.column('razza_codice',size=':2',name_long='!!Razza').relation('razza.codice',mode='foreignkey')
        tbl.column('ac','L',name_long='!!AC')
        tbl.column('ab','L',name_long='!!AB')
        tbl.column('forza','L',name_long='!!Forza')
        tbl.column('resistenza','L',name_long='!!Resistenza')
        tbl.column('fato','L',name_long='!!Fato')
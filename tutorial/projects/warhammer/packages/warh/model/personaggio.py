# encoding: utf-8

class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('personaggio',pkey='id',name_long='!!Personaggio',
                      name_plural='!!Personaggi')
        self.sysFields(tbl)
        tbl.column('nome',name_long='!!Nome')

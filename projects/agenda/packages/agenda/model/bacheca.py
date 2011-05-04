# encoding: utf-8

class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('bacheca',pkey='id',name_long='!!Bacheca',name_plural='!!Bacheche')
        self.sysFields(tbl)
        tbl.column('giorno',dtype='D',name_long='!!Giorno')
        tbl.column('ora',dtype='H',name_long='!!Ora')
        tbl.column('autore',name_long='!!Autore')
        tbl.column('titolo',name_long='!!Titolo')
        tbl.column('contenuto',size=':200',name_long='!!Contenuto')     
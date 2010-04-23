# encoding: utf-8

class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('diagnosi',pkey='codice',name_long='!!Diagnosi',
                      name_plural='!!Tabella',rowcaption='$descrizione')
        self.sysFields(tbl,id=False)
        tbl.column('codice',name_long='!!Codice')
        tbl.column('descrizione',name_long='!!Descrizione')

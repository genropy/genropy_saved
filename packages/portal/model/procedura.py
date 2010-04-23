# encoding: utf-8

class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('procedura',pkey='codice',name_long='!!Procedura',
                      name_plural='!!Procedura',rowcaption='$descrizione')
        self.sysFields(tbl,id=False)
        tbl.column('codice',name_long='!!Codice')
        tbl.column('descrizione',name_long='!!Descrizione')        

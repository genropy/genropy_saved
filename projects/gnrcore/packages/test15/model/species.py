# encoding: utf-8
from gnr.app.gnrdbo import GnrHTable

class Table(GnrHTable):
    def config_db(self, pkg):
        tbl =  pkg.table('species',pkey='id',name_long='!!Species',
                      name_plural='!!Species',df_fields='abilities')
        self.sysFields(tbl)
        self.htableFields(tbl)
        tbl.column('abilities',
                    dtype='X',
                    name_long = '!!Abilities')

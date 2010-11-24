# encoding: utf-8
from gnr.app.gnrdbo import GnrHTable
class Table(GnrHTable):
    def config_db(self, pkg):
        tbl =  pkg.table('datacatalog',  pkey='id',name_long='!!Model catalog',
                      name_plural='!!DC Elements',rowcaption='$description')
        self.sysFields(tbl)
        self.htableFields(tbl)
        
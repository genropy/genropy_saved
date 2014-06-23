# encoding: utf-8
from gnr.app.gnrdbo import GnrHTable

class Table(GnrHTable):
    def config_db(self, pkg):
        tbl = pkg.table('category', pkey='id', name_long='!!Category',
                        name_plural='!!Categories', rowcaption='$description')
        self.sysFields(tbl)
        self.htableFields(tbl)
        
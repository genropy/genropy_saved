# encoding: utf-8

class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('catalog',pkey='id',name_long='!!Catalog',
                      name_plural='!!Catalogs')
        self.sysFields(tbl)
        tbl.column('code',name_long='!!Code',indexed='y')
        tbl.column('description',name_long='!!Description')
        
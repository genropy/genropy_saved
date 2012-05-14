# encoding: utf-8

class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('customer',pkey='id',name_long='!!Customer',
                      name_plural='!!Customer')
        self.sysFields(tbl)
        tbl.column('name',name_long='!!Name')
        tbl.column('description',name_long='!!Description')
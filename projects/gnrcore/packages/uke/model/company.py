# encoding: utf-8

class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('company',pkey='id',name_long='!!Company',
                      name_plural='!!Company')
        self.sysFields(tbl)
        tbl.column('name',name_long='!!Name')
        tbl.column('description',name_long='!!Description')
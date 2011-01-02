# encoding: utf-8

class Table(object):
    def config_db(self, pkg):
        tbl = pkg.table('keyword', pkey='id', name_long='!!Keyword',
                        name_plural='!!Keywords')
        self.sysFields(tbl)
        tbl.column('name', name_long='!!Name')
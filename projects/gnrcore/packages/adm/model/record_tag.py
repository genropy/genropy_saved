# encoding: utf-8

class Table(object):
    def config_db(self, pkg):
        tbl = pkg.table('record_tag', pkey='id', name_long='!!Table tag',
                        name_plural='!!Table tags')
        self.sysFields(tbl)
        tbl.column('tablename', name_long='!!Table name')
        tbl.column('tag', name_long='!!Tag')
        tbl.column('description', name_long='!!Description')

# encoding: utf-8

class Table(object):
    def config_db(self, pkg):
        tbl = pkg.table('error', name_short='Err', name_long='Error', pkey='id')
        tbl.column('id', size='22')
        tbl.column('ts', 'DH', notnull='y')
        tbl.column('data')
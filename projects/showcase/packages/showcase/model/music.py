# encoding: utf-8

class Table(object):
    def config_db(self, pkg):
        tbl = pkg.table('music', pkey='id', name_long='!!Movie',
                        name_plural='!!Movies', rowcaption='$title')
        tbl.column('id', size='22', group='_', readOnly=True, name_long='Id')
        tbl.column('title', name_long='!!Title', validate_case='capitalize')
        tbl.column('genre', name_long='!!Genre', indexed=True)
        tbl.column('year', 'L', name_long='!!Year', indexed=True)
        tbl.column('op', name_long='!!Op.')
        tbl.column('number', 'L', name_long='!!Number')
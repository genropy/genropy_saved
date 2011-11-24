# encoding: utf-8

class Table(object):
    def config_db(self, pkg):
        tbl = pkg.table('person', pkey='id', rowcaption='$name',
                        name_long='!!Person', name_plural='!!Persons')
        tbl.column('id', size='22', group='_', readOnly=True, name_long='!!Id')
        tbl.column('name', name_long='!!Name')
        tbl.column('b_year', 'L', name_long='!!Birth Year')
        tbl.column('d_year', 'L', name_long='!!Death Year')
        tbl.column('nationality', name_long='!!Nationality')
        tbl.column('number', 'L', name_long='!!Number')
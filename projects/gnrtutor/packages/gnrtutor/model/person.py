# encoding: utf-8

class Table(object):
    def config_db(self, pkg):
        tbl = pkg.table('person', pkey='id', rowcaption='$name_full',
                        name_long='!!Person', name_plural='!!Persons',
                        virtual_columns='$name_full')
        tbl.column('id', size='22', group='_', readOnly=True, name_long='!!Id')
        tbl.column('name_first', name_long='!!First Name')
        tbl.column('name_last', name_long='!!Last Name')
        tbl.column('birth_year', 'L', name_long='!!Birth Year')
        tbl.column('death_year', 'L', name_long='!!Death Year')
        tbl.column('nationality', name_long='!!Nationality')
        tbl.column('number', 'L', name_long='!!Number')

        tbl.formulaColumn('name_full',"""COALESCE($name_first,'') || ' ' || COALESCE($name_last,'')""",name_long='Full Name')
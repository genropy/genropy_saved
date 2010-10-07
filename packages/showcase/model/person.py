# encoding: utf-8

class Table(object):
    def config_db(self, pkg):
        tbl = pkg.table('person',pkey='id',name_long='!!people',
                        #rowcaption='$name',
                        name_plural='!!People')
        tbl.column('id',size='22',group='_',readOnly=True,name_long='Id')
        tbl.column('name', name_short='N.', name_long='Name')
        tbl.column('year', 'L', name_short='Yr', name_long='Birth Year')
        tbl.column('nationality', name_short='Ntl',name_long='Nationality')
        tbl.column('number','L',name_long='!!Number')
        
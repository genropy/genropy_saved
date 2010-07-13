# encoding: utf-8

class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('movie',  pkey='id',name_long='!!Movie',
                        name_plural='!!Movies',rowcaption='$title')
        tbl.column('id',size='22',group='_',readOnly='y',name_long='Id')
        tbl.column('title', name_short='Ttl.',name_long='Title',
                    validate_case='capitalize', validate_len='3,40')
        tbl.column('genre', name_short='Gnr',name_long='Genre',
                            validate_case='upper', validate_len='3,10',indexed='y')
        tbl.column('year', 'L', name_short='Yr',name_long='Year',indexed='y')
        tbl.column('nationality', name_short='Ntl', name_long='Nationality')
        tbl.column('description', name_short='Dsc', name_long='Movie description')
        tbl.column('number','L',name_long='!!Number')
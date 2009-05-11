class Table(object):
    def config_db(self,pkg):
        tbl = pkg.table('movie', name_short='Mv',name_long='Movie',rowcaption='title', pkey='id')
        
        tbl.column('id',size='22',group='_',readOnly='y',name_long='Id')
        tbl.column('title', name_short='Ttl.',name_long='Title',
                                validate_case='capitalize', validate_len='3,40')

        tbl.column('genre_code', name_short='Gnr',name_long='Genre',size='4').relation('cinema.genre.code')
        
        tbl.column('year', 'L', name_short='Yr',name_long='Year',indexed='y')
        tbl.column('nationality', name_short='Ntl', name_long='Nationality')
        tbl.column('description', name_short='Dsc', name_long='Movie description')
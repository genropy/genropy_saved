class Table(object):
    def config_db(self,pkg):
        tbl = pkg.table('dvd', name_short='Dvd', name_long='Dvd', pkey='id')
        tbl.column('id',size='22',group='_',readOnly='y',name_long='Id')
        tbl.column('movie_id', name_short='Mid', name_long='Movie id').relation('movie.id')
        tbl.column('purchasedate', 'D', name_short='Pdt', name_long='Purchase date')
        
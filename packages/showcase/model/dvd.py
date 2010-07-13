# encoding: utf-8

class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('dvd',  pkey='id',name_long='!!Dvd',
                      name_plural='!!Dvd')
        tbl.column('id',size='22',group='_',readOnly='y',name_long='Id')
        tbl.column('movie_id', size='22',name_short='Mid', 
                    name_long='Movie id').relation('movie.id',mode='foreignkey')
        tbl.column('purchasedate', 'D', name_short='Pdt', name_long='Purchase date')
        tbl.column('available', name_short='Avl', name_long='Available')
        tbl.column('number','L',name_long='!!Number')
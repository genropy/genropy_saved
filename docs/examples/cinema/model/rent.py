class Table(object):
    def config_db(self,pkg):
        tbl = pkg.table('rent', name_short='Dvd', name_long='Dvd', pkey='rent')
        tbl.column('id', size='4')
        tbl.column('dvd_id', name_long='dvd id').relation('movie.id')
        tbl.column('pickup_date', 'D',  name_long='Pickup date')
        tbl.column('giveback_date', 'D',name_long='giveback date')
        tbl.column('user_id',size='22',name_long='User id').relation('adm.user.id')
        

class Table(object):
    def config_db(self,pkg):
        tbl = pkg.table('card', name_short='card', name_long='Cast', rowcaption='name,year:%s (%s)', pkey='id')
        tbl.column('id',size='22',group='_',readOnly='y',name_long='Id')
        tbl.column('firstname', name_short='N.', name_long='Name')
        tbl.column('lastname', name_short='N.', name_long='Last name')
        tbl.column('birthday', 'D', name_short='Bd', name_long='Birthday')
        tbl.column('nationality', name_short='Ntl',name_long='Nationality')
        tbl.column('occupation_id',size='22', name_short='Rl.',name_long='Role').relation('cinema.occupation.id')
        
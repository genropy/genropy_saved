class Table(object):
    def config_db(self,pkg):
        tbl = pkg.table('cast', name_short='cast', name_long='Movie cast', rowcaption='', pkey='id')
        tbl.column('id',size='22',group='_',readOnly='y',name_long='Id')
        tbl.column('movie_id',size='22', name_short='Mid', 
                               name_long='Movie id').relation('cinema.movie.id')
        tbl.column('card_id',size='22', name_long='Card id').relation('cinema.card.id')
        tbl.column('occupation_id',size='22', name_short='Rl.',name_long='Role').relation('cinema.occupation.id')
        tbl.column('prizes', name_short='Priz.',name_long='Prizes', size='40')
# encoding: utf-8

class Table(object):
    def config_db(self, pkg):
        tbl = pkg.table('cast',pkey='id',name_long='!!Cast',
                          name_plural='!!Casts',rowcaption='@person_id.name,@movie_id.title')
        tbl.column('id',size='22',group='_',readOnly=True,name_long='Id')
        tbl.column('movie_id',size='22', name_short='Mid', 
                    name_long='Movie id').relation('movie.id',mode='foreignkey')
        tbl.column('person_id',size='22',name_short='Prs', 
                    name_long='Person id').relation('person.id',mode='foreignkey')
        tbl.column('role', name_short='Rl.',name_long='Role')
        tbl.column('prizes', name_short='Priz.',name_long='Prizes', size='40')
        tbl.column('number','L',name_long='!!Number')
        
    def zoomUrl(self):
        return 'showcase/model/person'
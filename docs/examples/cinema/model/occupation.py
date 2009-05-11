class Table(object):
    def config_db(self,pkg):
        tbl = pkg.table('occupation', name_short='Genre', name_long='Genre', pkey='id')
        tbl.column('id',size='22',group='_',readOnly='y',name_long='Id')
        tbl.column('name',  name_long='Name')
        tbl.column('alias')

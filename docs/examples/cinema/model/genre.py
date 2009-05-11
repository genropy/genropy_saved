class Table(object):
    def config_db(self,pkg):
        tbl = pkg.table('genre', name_short='Genre', name_long='Genre', pkey='code')
        tbl.column('code',size='4',group='_',readOnly='y',name_long='Code')
        tbl.column('name',  name_long='Name')
        tbl.column('alias')

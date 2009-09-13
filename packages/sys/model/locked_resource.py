
class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('locked_resource',  pkey='id',name_long='!!Locked Resources',
                      name_plural='!!Messages')
        tbl.column('id',size='22',name_long='!!id')
        tbl.column('lock_ts','DH',name_long='!!Date and Time')
        tbl.column('lock_table',size=':64',name_long='!!Table')
        tbl.column('lock_pkey',size=':64',name_long='!!locked record')
        tbl.column('page_id',size='22',name_long='!!Page_id')
        tbl.column('connection_id',size='22',name_long='!!Connection_id')
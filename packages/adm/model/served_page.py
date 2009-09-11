# encoding: utf-8

class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('served_page',  pkey='page_id',name_long='!!Served page',
                      name_plural='!!Served pages')
        tbl.column('page_id',size='22',name_long='!!Page id')
        tbl.column('pagename',name_long='!!Page name')
        tbl.column('connection_id',size='22',group='_').relation('connection.id',mode='foreignkey',onDelete='cascade')
        tbl.column('start_ts','DH',name_long='!!Start ts')
        tbl.column('end_ts','DH',name_long='!!Start ts')
        tbl.column('subscribed_tables',name_long='!!Subscribed tables')
        tbl.column('aborted','B',name_long='!!Aborted')
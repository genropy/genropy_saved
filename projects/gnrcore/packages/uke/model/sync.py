# encoding: utf-8

class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('sync',pkey='id',name_long='!!Sync')
        self.sysFields(tbl)
        tbl.column('sync_utc','DH',name_long='!!Sync utc')
        tbl.column('sync_origin_id',name_long='!!Sync origin').relation('client_db.id',realtion_name='sync_items')

        tbl.column('sync_table',name_long='!!Table')
        tbl.column('sync_pkey',name_long='!!Sync table pkey')
        tbl.column('sync_event',name_long='!!Sync event')
        tbl.column('sync_data','X',name_long='!!Sync data')

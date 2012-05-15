# encoding: utf-8

class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('sync',pkey='id',name_long='!!Sync',
                      name_plural='!!Sync')
        self.sysFields(tbl)
        tbl.column('tablename',name_long='!!Table')
        tbl.column('event',name_long='!!Event',values='I,U,D')
        tbl.column('event_pkey',name_long='!!Pkey')
        tbl.column('event_data','X',name_long='!!Data')
        tbl.column('event_check_ts','H',name_long='!!Event check ts')
        tbl.column('status','L',name_long='!!Status') #0 updated, 1 to send, -1 conflict
        tbl.column('remote','B',name_long='!!Remote')
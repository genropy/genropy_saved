# encoding: utf-8

class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('connection',  pkey='id',name_long='!!Connection',
                      name_plural='!!Connections')
        tbl.column('id',size='22',name_long='!!Connection id')
        tbl.column('userid',size=':32',name_long='!!Userid').relation('user.username')
        tbl.column('username',size=':32',name_long='!!Username')
        tbl.column('ip',size=':15',name_long='!!Ip number')
        tbl.column('start_ts','DH',name_long='!!Start TS')
        tbl.column('end_ts','DH',name_long='!!Start TS')
        tbl.column('user_agent',name_long='!!User agent')
        
    #def trigger_onUpdating(self, record, old_record=None):
    #    pass
    #
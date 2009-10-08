# encoding: utf-8
from datetime import datetime

class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('connection',  pkey='id',name_long='!!Connection',
                      name_plural='!!Connections', broadcast = True)
        tbl.column('id',size='22',name_long='!!Connection id')
        tbl.column('userid',size=':32',name_long='!!Userid').relation('user.username')
        tbl.column('username',size=':32',name_long='!!Username')
        tbl.column('ip',size=':15',name_long='!!Ip number')
        tbl.column('start_ts','DH',name_long='!!Start TS')
        tbl.column('end_ts','DH',name_long='!!Start TS')
        tbl.column('end_reason',size=':12',name_long='!!End reason')
        tbl.column('user_agent',name_long='!!User agent')
        tbl.aliasColumn('user_fullname',relation_path='@userid.fullname',name_long='!!User fullname')
        
        
    def trigger_onUpdating(self, record, old_record=None):
        if 'end_ts' in record and record['end_ts']:
            self.db.table('adm.served_page').closePendingPages(connection_id=record['id'],
                                             end_ts=record['end_ts'],
                                             end_reason=record['end_reason'])
    def getPendingConnections(self,userid=None):
        where='$end_ts is null'
        if userid:
            where='%s AND %s' % ('$userid=:userid',where)
        return self.query(where=where,userid=userid).fetch()
        
    def closePendingConnections(self, end_ts=None, end_reason=None):
        end_ts=end_ts or datetime.now()
        for conn in self.getPendingConnections():
            self.closeConnection(conn['id'],end_ts=end_ts,end_reason=end_reason)
            
    def closeConnection(self,connection_id,end_ts=None, end_reason=None):
        self.update(dict(id=connection_id,end_ts=end_ts or datetime.now(),end_reason=end_reason))
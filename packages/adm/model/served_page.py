# encoding: utf-8
import datetime

class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('served_page',  pkey='page_id',name_long='!!Served page',
                      name_plural='!!Served pages')
        tbl.column('page_id',size='22',name_long='!!Page id')
        tbl.column('pagename',name_long='!!Page name')
        tbl.column('connection_id',size='22',group='_').relation('connection.id',mode='foreignkey',onDelete='cascade')
        tbl.column('start_ts','DH',name_long='!!Start ts')
        tbl.column('end_ts','DH',name_long='!!Start ts')
        tbl.column('end_reason',size=':12',name_long='!!End Reason')
        tbl.column('subscribed_tables',name_long='!!Subscribed tables')
        
    def getPendingPages(self,connection_id=None):
        where='$end_ts is null'
        if connection_id:
            where='%s AND %s' % ('$connection_id=:connection_id',where)
        return self.query(where=where,connection_id=connection_id).fetch()
        
    def closePendingPages(self,connection_id=None,end_ts=None,end_reason=None):
        for page in self.getPendingPages(connection_id=connection_id):
            self.closePage(page['page_id'],end_ts=end_ts,end_reason=end_reason)
            
    def closePage(self,page_id,end_ts=None,end_reason=None):
        self.update(dict(page_id=page_id,end_ts=end_ts or datetime.now(),end_reason=end_reason))
        
        
            
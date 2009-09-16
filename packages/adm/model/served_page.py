# encoding: utf-8
from datetime import datetime

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
        
    def getLivePages(self,connection_id=None,topic=None,current_page_id=None):
        where=['$end_ts is null']
        if connection_id:
            where.append('$connection_id=:connection_id')
        if topic:
            where.append('$subscribed_tables ILIKE :topic')
        if current_page_id:
            where.append('$page_id!=:current_page_id')
            
        return self.query(where=' AND '.join(where),
                        connection_id=connection_id,
                        topic="%%%s%%"%(topic or ''),
                        current_page_id=current_page_id).fetch()
        
    def closePendingPages(self,connection_id=None,end_ts=None,end_reason=None):
        for page in self.getLivePages(connection_id=connection_id):
            self.closePage(page['page_id'],end_ts=end_ts,end_reason=end_reason)
            
    def closePage(self,page_id,end_ts=None,end_reason=None):
        self.update(dict(page_id=page_id,end_ts=end_ts or datetime.now(),end_reason=end_reason))

            
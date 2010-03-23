# encoding: utf-8
from __future__ import with_statement
from datetime import datetime

class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('message',  pkey='id',name_long='!!Messages',
                      name_plural='!!Messages')
        tbl.column('id',size='22',name_long='!!id')
        tbl.column('datetime','DH',name_long='!!Date and Time')
        tbl.column('expiry','DH',name_long='!!Expiry')
        tbl.column('dst_page_id',size='22',name_long='!!Destination page_id',indexed=True)
        tbl.column('dst_user',size=':32',name_long='!!Destination user',indexed=True)
        tbl.column('dst_connection_id',size='22',name_long='!!Connection Id',indexed=True)
        tbl.column('src_page_id',size='22',name_long='!!Source page_id',indexed=True)
        tbl.column('src_user',size=':32',name_long='!!Source user',indexed=True)
        tbl.column('src_connection_id',size='22',name_long='!!Source Connection Id',indexed=True)
        tbl.column('message_type',size=':12',name_long='!!Message Type')
        tbl.column('body',dtype='X',name_long='!!Message body')
        
    def getMessages(self, connection_id, user, page_id):
        with self.db.tempEnv(connectionName='system'): 
            fetch = self.query('*,body',where="""($dst_connection_id=:connection_id OR $dst_user=:user OR $dst_page_id=:page_id) 
                                                    AND ($expiry IS NULL OR $expiry >:curr_time)""", connection_id=connection_id,
                                                    user=user, page_id=page_id, curr_time=datetime.now()).fetch()
            return fetch
        
    def writeMessage(self, body=None, connection_id=None, user=None, page_id=None, expiry=None, message_type=None):
        srcpage = self.db.application.site.currentPage
        record = dict(
            body=body,
            dst_connection_id=connection_id,
            dst_user=user,
            dst_page_id=page_id,
            expiry=expiry,
            message_type=message_type,
            datetime=datetime.now(),
            src_connection_id=srcpage.connection.connection_id,
            src_page_id=srcpage.page_id,
            src_user=srcpage.user)
            
        with self.db.tempEnv(connectionName='system'): 
            if isinstance(page_id,list):
                sent_messages_id_list=[]
                for p in page_id:
                    record['dst_page_id']=p
                    self.insert(record)
                    sent_messages_id_list.append(record['id'])
                    record['id'] = None
                result = sent_messages_id_list
            else:
                self.insert(record)
                result = record['id']
            self.db.commit()
            return result
            
    def deleteMessage(self, message_id):
        with self.db.tempEnv(connectionName='system'):
            self.delete(dict(id=message_id))
            self.db.commit()

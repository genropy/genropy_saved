#!/usr/bin/env python
# encoding: utf-8
from gnr.core.gnrbag import Bag

class Table(object):
    def config_db(self, pkg):
        tbl = pkg.table('error', pkey='id', name_long='Debug Error', name_plural='!!Errors',caption_field='description',rowcaption='$error_type,$description')
        self.sysFields(tbl)
        tbl.column('description',name_long='!!Description')
        tbl.column('error_data',dtype='X',name_long='!!Traceback')

        tbl.column('username',name_long='User')
        tbl.column('user_ip',name_long='User ip')

        tbl.column('user_agent',name_long='User agent')

        tbl.column('fixed',name_long='Fixed')
        tbl.column('notes',name_long='Notes')
        tbl.column('error_type',name_long='!!Error type',values='ERR:Error,EXC:Exception')


    def writeException(self,description=None,traceback=None,user=None,user_ip=None,user_agent=None):
        rec = dict(description=description,error_data=traceback,username=user,user_ip=user_ip,user_agent=user_agent,error_type='EXC')
        with self.db.tempEnv(connectionName='system',storename=self.db.rootstore):
            self.insert(rec)
            self.db.commit()
        return rec

    def writeError(self,description=None,error_type=None,user=None,user_ip=None,user_agent=None,**kwargs):
        error_data = Bag(self.db.currentEnv)
        error_data.update(kwargs)
        rec = dict(description=description,error_data=error_data,username=user,user_ip=user_ip,user_agent=user_agent,error_type=error_type or 'ERR')
        with self.db.tempEnv(connectionName='system',storename=self.db.rootstore):
            self.insert(rec)
            self.db.commit()
        return rec
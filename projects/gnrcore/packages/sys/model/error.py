#!/usr/bin/env python
# encoding: utf-8

class Table(object):
    def config_db(self, pkg):
        tbl = pkg.table('error', pkey='id', name_long='Error', name_plural='!!Errors',caption_field='description')
        self.sysFields(tbl)
        tbl.column('description',name_long='!!Description')
        tbl.column('traceback',dtype='X',name_long='!!Traceback')

        tbl.column('username',name_long='User')
        tbl.column('user_ip',name_long='User ip')

        tbl.column('user_agent',name_long='User agent')

        tbl.column('fixed',name_long='Fixed')
        tbl.column('notes',name_long='Notes')


    def writeException(self,description=None,traceback=None,user=None,user_ip=None,user_agent=None):
        rec = dict(description=description,traceback=traceback,username=user,user_ip=user_ip,user_agent=user_agent)
        with self.db.tempEnv(connectionName='system',storename=self.db.rootstore):
            self.insert(rec)
            self.db.commit()
        return rec
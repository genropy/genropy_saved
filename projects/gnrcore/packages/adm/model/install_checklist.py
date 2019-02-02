#!/usr/bin/env python
# encoding: utf-8
from builtins import object
from datetime import datetime

class Table(object):
    def config_db(self,pkg):
        tbl = pkg.table('install_checklist', pkey='__syscode', 
                    name_long='!!Install checklist', 
                    name_plural='!!Install checklist',caption_field='description')
        self.sysFields(tbl,id=False,ins=False,upd=False)
        tbl.column('name', name_long = '!!Name')
        tbl.column('description', name_long = '!!Description')
        tbl.column('pkg',size = ':20', name_long = '!!Package')
        tbl.column('checked', dtype = 'B' , name_long = '!!Checked')
        tbl.column('check_ts', dtype = 'DH' , name_long = '!!Check ts')
        tbl.column('check_user',size = ':30', name_long = '!!Check user')
        tbl.column('annotations', name_long = '!!Annotations')
        tbl.column('doc_url', name_long='!!Documentation url', name_short='!!Url')
        
    def trigger_onUpdating(self,record,old_record):
        if record['checked']:
            record['check_ts'] = datetime.now()
            record['check_user'] = self.db.currentEnv['user']
        else:
            record['check_ts'] = None
            record['check_user'] = None

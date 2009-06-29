#!/usr/bin/env python
# encoding: utf-8

import os
from gnr.core.gnrlang import getUuid

class Table(object):
   
    def config_db(self, pkg):
        tbl =  pkg.table('user',  pkey='id', name_long='!!User', rowcaption='username,email:%s (%s)')
        self.sysFields(tbl,ins=True, upd=True, md5=True)
        tbl.column('id',size='22',group='_',readOnly='y',name_long='Id')
        tbl.column('username', size=':32',name_long='!!Username', unique='y', 
                    indexed='y',validate_notnull=True,validate_notnull_error='!!Mandatory field')
        tbl.column('email',name_long='Email',validate_notnull=True,
                    validate_notnull_error='!!Mandatory field')
        tbl.column('firstname', size=':32',name_long='!!First name',
                    validate_notnull=True,validate_case='c',validate_notnull_error='!!Mandatory field')
        tbl.column('lastname', size=':32',name_long='!!Last name',
                    validate_notnull=True,validate_case='c',validate_notnull_error='!!Mandatory field')
        tbl.column('registration_date', 'D' ,name_long='!!Registration Date')
        tbl.column('auth_tags', name_long='!!Authorization Tags')
        tbl.column('status', name_long='!!Status', size='4',
                          validate_values_conf='!!Confirmed',
                          validate_values_wait='!!Waiting'
                          )
        tbl.column('md5pwd', name_long='!!PasswordMD5', size=':65')
        tbl.column('locale', name_long='!!Default Language', size=':12')
        tbl.column('preferences', dtype='X', name_long='!!Preferences')

    def createPassword(self):
        password=getUuid()[0:6]
        return password
        
    def populate(self, fromDump=None):
        if fromDump:
            dump_folder = os.path.join(self.db.application.instanceFolder,'dumps')
            self.importFromXmlDump(dump_folder)
    
    def getPreference(self, record, package, name):
        record = self.recordAs(record, mode='bag')
        return record['preferences'].getItem('%s.%s' % (package,name))
        
    def setPreference(self, record, package, name, value):
        record = self.recordAs(record, mode='bag')
        record['preferences'].setItem('%s.%s' % (package,name,value))
        self.update(record)
        self.db.commit()
        
        
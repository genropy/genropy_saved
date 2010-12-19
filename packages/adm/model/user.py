#!/usr/bin/env python
# encoding: utf-8
from __future__ import with_statement
import os
from gnr.core.gnrlang import getUuid
from gnr.core.gnrbag import Bag

class Table(object):
   
    def config_db(self, pkg):
        tbl =  pkg.table('user',  pkey='id', name_long='!!User', rowcaption='username,email:%s (%s)',tabletype='main')
        self.sysFields(tbl,ins=True, upd=True, md5=True)
        tbl.column('id',size='22',group='_',readOnly='y',name_long='Id')
        tbl.column('username', size=':32',name_long='!!Username', unique='y', _sendback=True,
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
                          validate_values_wait='!!Waiting')
        tbl.column('md5pwd', name_long='!!PasswordMD5', size=':65')
        tbl.column('locale', name_long='!!Default Language', size=':12')
        tbl.column('preferences', dtype='X', name_long='!!Preferences')
        tbl.formulaColumn('fullname', "$firstname||' '||$lastname", name_long=u'!!Name')

    def createPassword(self):
        password=getUuid()[0:6]
        return password
        
    def trigger_onUpdating(self, record,**kwargs):
        self.passwordTrigger(record)
        
    def trigger_onInserting(self, record,**kwargs):
        self.passwordTrigger(record)
        
    def passwordTrigger(self,record):
        if 'md5pwd' in record:
            password =record['md5pwd']
            if len(password)<32:
                record['md5pwd']=self.db.application.changePassword(None, None, password, userid=record['username'])
            
    def populate(self, fromDump=None):
        if fromDump:
            dump_folder = os.path.join(self.db.application.instanceFolder,'dumps')
            self.importFromXmlDump(dump_folder)
    
    def getPreference(self,path='', pkg='',dflt='',username=''):
        result = self.loadRecord(username)['preferences'] 
        if result and path!='*':
            result = result['%s.%s' %(pkg,path)]           
        return result or dflt
            
    def setPreference(self,path='',data='', pkg='',username=''):
        with self.db.tempEnv(connectionName='system'):
            record = self.loadRecord(username,for_update=True)
            record['preferences.%s.%s' %(pkg,path)] = data
            self.update(record)
            self.db.commit()
        
    def loadRecord(self,username,for_update=False):
        try:
            record = self.record(username=username,for_update=for_update).output('bag')
        except:
            record = Bag()
        return record

        
        

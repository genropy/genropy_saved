# encoding: utf-8
from gnr.core.gnrbag import Bag
class Table(object):        
    def config_db(self, pkg):
        tbl =  pkg.table('audit',pkey='id',name_long='!!Audit',name_plural='!!Audit')
        self.sysFields(tbl)
        tbl.column('tablename',name_long='!!Table name')
        tbl.column('event',size='1',name_long='!!Change type',
                    values='I:Insert,U:Update,D:Delete')
        tbl.column('username',name_long='!!User')
        tbl.column('record_pkey',name_long='!!Record Pkey')
        tbl.column('version','L',name_long='!!Version')
        tbl.column('data','X',name_long='!!Data')
        tbl.column('transaction_id',name_long='!!Transaction id')
    
    def getXmlRecord(self,record=None):
        if not isinstance(record,Bag):
            record = Bag(record)
        return record.toXml()
    

    def audit(self,tblobj,event,audit_mode=None,record=None,old_record=None,username=None,page=None):
        if event=='I' and audit_mode=='lazy':
            return
        if not username:
            username = self.db.currentEnv.get('user') 
        version = record.get('__version',0)
        audit_record = dict(tablename=tblobj.fullname,event=event,username=username,
                      record_pkey=record[tblobj.pkey],version=version,transaction_id=self.db.currentEnv.get('env_transaction_id'))
        if event == 'I' or event=='D':
            audit_record['data'] = self.getXmlRecord(record)
        if event == 'U':
            assert old_record, 'Missing old_record in an update that uses audit feature tbl: %s' %tblobj.fullname
            changes = Bag()
            for k in record.keys():
                if k in ('__version','__mod_ts'):
                    continue
                if record[k] != old_record.get(k):
                    changes[k] = record[k]
            audit_record['data'] = changes.toXml()
            if audit_mode=='lazy' and version==1:
                first_audit = dict(audit_record)
                first_audit['version'] = 0
                first_audit['event'] = 'I'
                first_audit['data'] = self.getXmlRecord(old_record)
                self.insert(first_audit)
        self.insert(audit_record)

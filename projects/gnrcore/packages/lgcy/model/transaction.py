# encoding: utf-8

from datetime import datetime
from gnr.core.gnrlang import GnrException,tracebackBag


class Table(object):
    def config_db(self,pkg):
        tbl=pkg.table('transaction', pkey='id', name_long='!!Transaction', name_plural='!!Transaction',caption_field='description')
        self.sysFields(tbl)
        tbl.column('tbl', name_long='!!DB table')
        tbl.column('description', name_long='!!Description')
        tbl.column('data', dtype='X', name_long='!!Data')
        tbl.column('write_ts', dtype='DH', name_long='!!Write ts')
        tbl.column('errors', dtype='X', name_long='!!Errors')
        tbl.column('errors_ts', dtype='DH', name_long='!!Errors ts')
        tbl.column('send_ts', dtype='DH', name_long='!!Send ts')


    def trigger_onUpdating(self,record,old_record=None):
        for c,cobj in self.columns.items():
            if cobj.relatedTable() and self.fieldsChanged(c,record,old_record):
                if record.get(c):
                    record['write_ts'] = record['__mod_ts']
                else:
                    record['write_ts'] = None
                break
    
    
    def storeTransaction(self,tbl=None,data=None,description=None,send_ts=None):
        transaction_class = self.db.table(tbl).lgcy_transactionDescriptor()
        if not transaction_class:
            return
        try:
            transaction = transaction_class(data)
        except GnrException as e:
            return {'validation_error':str(e),'description':description,'ts':datetime.now()}
        transaction_record = self.newrecord(data=data,description=description,tbl=tbl,send_ts=send_ts)
        self.insert(transaction_record)
        return {'transaction_id':transaction_record['id'],'transaction_ts':transaction_record['__ins_ts']}
    
    def loadTransaction(self,transaction_id):
        record = self.recordAs(transaction_id,'record')
        return self.db.table(record['tbl']).lgcy_transactionDescriptor(record['data'])
    
    def writeTransaction(self,transaction_id):
        with self.recordToUpdate(transaction_id) as rec:
            try:
                self.loadTransaction(rec).write()
                rec['write_ts'] = datetime.now()
            except Exception as e:
                rec['errors'] = tracebackBag()
                rec['errors_ts'] = datetime.now()
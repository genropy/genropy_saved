# encoding: utf-8
from gnr.core.gnrbag import Bag

class Table(object):
    def config_db(self,pkg):
        tbl=pkg.table('dbchange', pkey='ref', name_long='!!Dbchange', name_plural='!!Db change')
        self.sysFields(tbl,id=False,ins=True, upd=False, ldel=False)
        tbl.column('ref', dtype='serial', name_long='!!Reference')
        tbl.column('tbl', size=':80', name_long='!!Table')
        tbl.column('record_pkey', name_long='!!Record pkey')
        tbl.column('evt', size='1',name_long='Evt', name_short='!!Evt')
        tbl.column('record', dtype='X', name_long='!!Record')
        tbl.column('dbstore', size=':60', name_long='!!Dbstore')
        
    
    def logChange(self,tblobj,evt=None,record=None):
        if not isinstance(record, Bag):
            record = Bag(record)
        self.insert(dict(tbl=tblobj.fullname,evt=evt,
                        dbstore=self.db.currentEnv.get('storename'),
                        record=record,record_pkey=record[tblobj.pkey]))
    
    def checkPkey(self, record):
        pass

    

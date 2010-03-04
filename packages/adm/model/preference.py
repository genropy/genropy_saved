# encoding: utf-8
from gnr.core.gnrbag import Bag

class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('preference',pkey='code',name_long='!!Preference',
                      name_plural='!!Preference')
        self.sysFields(tbl,id=False)
        tbl.column('code',size='12',name_long='!!Code')
        tbl.column('data','X',name_long='!!Data')        
        
    def getPreference(self):
        with self.db.tempEnv(connectionName='system'):
            record = self.record(pkey='_mainpref_', ignoreMissing=True).output('bag')
            if not record['code']:
                record = Bag(dict(code='_mainpref_'))
                self.insert(record)
                self.db.commit()
        return record['data']
    
    def setPreference(self,data):
        with self.db.tempEnv(connectionName='system'):
            record = self.record(pkey='_mainpref_', for_update=True).output('bag')
            record['data'] = data
            self.update(record)
            self.db.commit()

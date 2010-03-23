# encoding: utf-8
from __future__ import with_statement
from gnr.core.gnrbag import Bag

class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('preference',pkey='code',name_long='!!Preference',
                      name_plural='!!Preference')
        self.sysFields(tbl,id=False)
        tbl.column('code',size='12',name_long='!!Code')
        tbl.column('data','X',name_long='!!Data')        
        
    def getPreference(self, path, pkg='',dflt=''):
        return self.loadPreference()['data.%s.%s' %(pkg,path)] or dflt
    
    def setPreference(self, path, data, pkg=''):
        record = self.loadPreference(for_update=True) or self.newPreference()
        record['data.%s.%s' %(pkg,path)]=data
        self.savePreference(record)
            
    def loadPreference(self, for_update=False):
        with self.db.tempEnv(connectionName='system'):
            record = self.record(pkey='_mainpref_', ignoreMissing=True, for_update=for_update).output('bag')
        if not record['code']:
            record=None
        return record
    def newPreference(self):
        with self.db.tempEnv(connectionName='system'):
            record = Bag(dict(code='_mainpref_', data=Bag()))
            self.insert(record)
            self.db.commit()
        return record
    
    def savePreference(self, record):
        with self.db.tempEnv(connectionName='system'):
            self.update(record)
            self.db.commit()

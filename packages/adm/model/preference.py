# encoding: utf-8
from gnr.core.gnrbag import Bag
class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('preference',pkey='code',name_long='!!Preference',
                      name_plural='!!Preference')
        self.sysFields(tbl,id=False)
        tbl.column('code',size='12',name_long='!!Code')
        tbl.column('data','X',name_long='!!Data')        
        
    
    def getPrefRecord(self,code=None,autocreate=False):
        record = self.record(pkey=code, ignoreMissing=True).output('bag')
        if autocreate and not record['code']:
            record = Bag(dict(code=code))
            self.insert(record)
            self.db.commit()
        return record
# encoding: utf-8

class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('subscription',pkey='id',name_long='!!Subscription',
                      name_plural='!!Subscriptions')
        self.sysFields(tbl)
        tbl.column('tablename',name_long='!!Tablename') #table fullname 
        #tbl.column('rec_pkey',name_long='!!Pkey') # if rec_pkey == * means all records
        tbl.column('dbstore',name_long='!!Store')
        
    
    def copyRecords(self,table,pkey,dbstore):
        tblobj = self.db.table(table)
        queryargs = dict()
        if pkey!='*':
            queryargs = dict(where='$pkey=:pkey',pkey=pkey)
        records = tblobj.query(addPkeyColumn=False,**queryargs).fetch()
        with self.db.tempEnv(storename=dbstore):
            for rec in records:
                tblobj.insertOrUpdate(rec)
    
    def addSubscription(self,table=None,pkey=None,dbstore=None):
        pkeyname = self.db.table(table).pkey
        fkey='%s_%s' %(table.replace('.','_'),pkeyname)
        record = dict(dbstore=dbstore,tablename=table)
        record[fkey] = pkey
        self.insert(record)
        self.copyRecords(table=table,pkey=pkey or '*',dbstore=dbstore)
        
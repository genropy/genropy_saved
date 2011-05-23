# encoding: utf-8

class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('subscription',pkey='id',name_long='!!Subscription',
                      name_plural='!!Subscriptions')
        self.sysFields(tbl)
        tbl.column('tablename',name_long='!!Tablename') #table fullname 
        tbl.column('rec_pkey',name_long='!!Pkey') # if rec_pkey == * means all records
        tbl.column('dbstore',name_long='!!Store')
        
    def trigger_onInserting(self, record_data):
        """
        when we add a subscription we must copy data from main db to a store
        """
        self.copyRecords(table=record_data['tablename'],
                         pkey=record_data['rec_pkey'],
                        dbstore=record_data['dbstore'])
    
    def copyRecords(self,table,pkey,dbstore):
        tblobj = self.db.table(table)
        queryargs = dict()
        if pkey!='*':
            queryargs = dict(where='$pkey=:pkey',pkey=pkey)
        records = tblobj.query(addPkeyColumn=False,**queryargs).fetch()
        with self.db.tempEnv(storename=dbstore):
            for rec in records:
                tblobj.insertOrUpdate(rec)
        
        
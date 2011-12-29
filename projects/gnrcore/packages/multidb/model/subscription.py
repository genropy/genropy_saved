# encoding: utf-8
from gnr.core.gnrbag import Bag

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
                tblobj.insertOrUpdate(Bag(dict(rec)))
    
    def addSubscription(self,table=None,pkey=None,dbstore=None):
        fkey = self.tableFkey(table)
        record = dict(dbstore=dbstore,tablename=table)
        record[fkey] = pkey
        self.insert(record)
        self.copyRecords(table=table,pkey=pkey or '*',dbstore=dbstore)
        
    def tableFkey(self,table):
        if isinstance(table,basestring):
            table = self.db.table(table)
        return '%s_%s' %(table.fullname.replace('.','_'),table.pkey)
        
    def onSubscriberTrigger(self,tblobj,record,old_record=None,event=None):
        if not self.db.usingRootstore():
            return
        fkeyname = self.tableFkey(tblobj)
        pkey = record[tblobj.pkey]
        tablename = tblobj.fullname
        if tblobj.attributes.get('multidb_allRecords'):
            subscribedStores = self.db.dbstores.keys()
        else:
            subscribedStores = self.query(where='$tablename=:tablename AND $%s=:pkey' %(fkeyname,fkeyname),
                                    columns='$dbstore',addPkeyColumn=False,
                                    tablename=tablename,pkey=pkey,distinct=True).fetch()
            subscribedStores = [s['dbstore'] for s in subscribedStores]
        for storename in subscribedStores:
            requireCommit = False
            with self.db.tempEnv(storename=storename,_systemDbEvent=True):
                if event == 'I':
                    tblobj.insert(record)
                    requireCommit = True
                else:
                    f = tblobj.query(where='$%s=:pkey' %tblobj.pkey,pkey=pkey,for_update=True).fetch()
                    if f:
                        if event=='U':
                            tblobj.update(record,old_record=f[0])
                        else:
                            tblobj.delete(record)
                        requireCommit = True
                    elif event=='U':
                        tblobj.insert(record)   
                        requireCommit = True 
            if requireCommit:
                self.db.currentEnv.setdefault('_storesToCommit',set()).add(storename)
                    
                        
    

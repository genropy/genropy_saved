# encoding: utf-8
from gnr.core.gnrbag import Bag
from gnr.core.gnrdecorator import public_method

class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('subscription',pkey='id',name_long='!!Subscription',
                      name_plural='!!Subscriptions',broadcast='tablename,dbstore',ignoreUnify=True)
        self.sysFields(tbl)
        tbl.column('tablename',name_long='!!Tablename') #table fullname 
        #tbl.column('rec_pkey',name_long='!!Pkey') # if rec_pkey == * means all records
        tbl.column('dbstore',name_long='!!Store')
    
    def checkSubscribedRecord(self,table=None,pkey=None,dbstore=None):
        sub_record = dict()
        fkey = self.tableFkey(table)
        sub_record['tablename'] = table
        sub_record[fkey] = pkey
        sub_record['dbstore'] = dbstore
        if self.checkDuplicate(**sub_record):
            return
        self.insert(sub_record)
        
    def copyRecords(self,table,dbstore=None,pkeys=None):
        tblobj = self.db.table(table)
        queryargs = dict()
        if pkeys:
            queryargs = dict(where='$pkey IN :pkeys',pkeys=pkeys)
        if tblobj.attributes.get('hierarchical'):
            queryargs.setdefault('order_by','$hierarchical_pkey')
        records = tblobj.query(addPkeyColumn=False,bagFields=True,excludeLogicalDeleted=False,**queryargs).fetch()
        with self.db.tempEnv(storename=dbstore):
            for rec in records:
                tblobj.insertOrUpdate(Bag(dict(rec)))
            self.db.deferredCommit()  
    
    @public_method
    def addRowsSubscription(self,table,pkeys=None,dbstore=None):
        for pkey in pkeys:
            self.addSubscription(table,pkey=pkey,dbstore=dbstore)
        self.db.commit()
    
    def addSubscription(self,table=None,pkey=None,dbstore=None):
        tblobj = self.db.table(table)
        fkey = self.tableFkey(tblobj)
        record = dict(dbstore=dbstore,tablename=table)
        record[fkey] = pkey
        handler = getattr(tblobj,'onAddSubscription',None)
        if handler:
            handler(pkey,dbstore)
        if not self.checkDuplicate(**dict(record)):
            self.insert(record)

    
    @public_method
    def delRowsSubscription(self,table,pkeys=None,dbstore=None):
        for pkey in pkeys:
            self.delSubscription(table,pkey=pkey,dbstore=dbstore)
        self.db.commit()
    
    def delSubscription(self,table=None,pkey=None,dbstore=None):
        fkey = self.tableFkey(table)        
        f = self.query(where='$dbstore=:dbstore AND $tablename=:tablename AND $%s =:fkey' %fkey,for_update=True,
                            excludeLogicalDeleted=False,
                            dbstore=dbstore,tablename=table,fkey=pkey,addPkeyColumn=False).fetch()
        if f:
            self.delete(f[0])
    
    def trigger_onInserted(self,record):
        self.syncStore(record,'I')
    
    def trigger_onUpdated(self,record,old_record=None):
        self.syncStore(record,'U')

    def trigger_onDeleted(self,record):        
        self.syncStore(record,'D')

    def cloneSubscriptions(self,table,sourcePkey,destPkey):
        sourcestores = self.query(where="""$tablename=:t AND $%s =:fkey""" %self.tableFkey(table),t=table,fkey=sourcePkey,columns='$dbstore').fetch()
        for store in sourcestores:
            self.addSubscription(table=table,pkey=destPkey,dbstore=store['dbstore'])

    def syncStore(self,subscription_record=None,event=None,storename=None,tblobj=None,pkey=None):
        if subscription_record:
            table = subscription_record['tablename']
            pkey = subscription_record[self.tableFkey(table)]
            tblobj = self.db.table(table)
            storename = subscription_record['dbstore']
        if not self.db.dbstores.get(storename):
            return
        data_record = tblobj.query(where='$%s=:pkey' %tblobj.pkey,pkey=pkey,addPkeyColumn=False,bagFields=True,excludeLogicalDeleted=False).fetch()
        if data_record:
            data_record = data_record[0]
        else:
            return
        with self.db.tempEnv(storename=storename,_systemDbEvent=True):
            f = tblobj.query(where='$%s=:pkey' %tblobj.pkey,pkey=pkey,for_update=True,addPkeyColumn=False,excludeLogicalDeleted=False).fetch()
            if event == 'I':
                if not f:
                    tblobj.insert(data_record)
                else:
                    tblobj.update(data_record,f[0])
                self.db.deferredCommit()
            else:
                if f:
                    if event=='U':
                        tblobj.update(data_record,old_record=f[0])
                    else:
                        tblobj.delete(data_record)
                    self.db.deferredCommit()
                elif event=='U':
                    tblobj.insert(data_record)   
                    self.db.deferredCommit()
                    
    def onPlugToForm(self,field):
        if self.db.currentPage.dbstore:
            return False
        return dict(lbl_color='red')
        
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
        subscribedStores = []
        if tblobj.attributes.get('multidb_forcedStore'):
            store = tblobj.multidb_getForcedStore(record)
            if store:
                subscribedStores.append(store)
        elif tblobj.attributes.get('multidb_allRecords') or record.get('__multidb_default_subscribed'):
            subscribedStores = self.db.dbstores.keys()
        else:
            subscribedStores = self.query(where='$tablename=:tablename AND $%s=:pkey' %fkeyname,
                                    columns='$dbstore',addPkeyColumn=False,
                                    tablename=tablename,pkey=pkey,distinct=True).fetch()                
            subscribedStores = [s['dbstore'] for s in subscribedStores]
        for storename in subscribedStores:
            self.syncStore(event=event,storename=storename,tblobj=tblobj,pkey=pkey)
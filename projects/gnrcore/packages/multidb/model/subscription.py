# encoding: utf-8
from past.builtins import basestring
from builtins import object
from gnr.core.gnrbag import Bag
from gnr.core.gnrdecorator import public_method
from copy import deepcopy


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
        with self.db.tempEnv(storename=dbstore,_multidbSync=True):
            for rec in records:
                tblobj.insertOrUpdate(Bag(dict(rec)))
    
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
            self.db.table(table).syncChildren(pkey)
    
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

   #def cloneSubscriptions(self,table,sourcePkey,destPkey):
   #    sourcestores = self.query(where="""$tablename=:t AND $%s =:fkey""" %self.tableFkey(table),t=table,fkey=sourcePkey,columns='$dbstore').fetch()
   #    for store in sourcestores:
   #        self.addSubscription(table=table,pkey=destPkey,dbstore=store['dbstore'])

    def syncStore(self,subscription_record=None,event=None,storename=None,
                  tblobj=None,pkey=None,master_record=None,master_old_record=None,mergeUpdate=None):
        if subscription_record:
            table = subscription_record['tablename']
            pkey = subscription_record[self.tableFkey(table)]
            tblobj = self.db.table(table)
            storename = subscription_record['dbstore']
        if not self.db.dbstores.get(storename):
            return
        if master_record:
            data_record = deepcopy(master_record)
        else:
            data_record = tblobj.query(where='$%s=:pkey' %tblobj.pkey,pkey=pkey,addPkeyColumn=False,bagFields=True,excludeLogicalDeleted=False).fetch()
            if data_record:
                data_record = dict(data_record[0])
            else:
                return
        with self.db.tempEnv(storename=storename,_systemDbEvent=True,_multidbSync=True):
            f = tblobj.query(where='$%s=:pkey' %tblobj.pkey,pkey=pkey,for_update=True,
                            addPkeyColumn=False,bagFields=True,excludeLogicalDeleted=False).fetch()
            if event == 'I':
                if not f:
                    tblobj.insert(data_record)
                else:
                    tblobj.update(data_record,f[0])
            else:
                if f:
                    old_record = f[0]
                    if event=='U':
                        updater = data_record
                        if mergeUpdate:
                            updater = {}
                            for k,v in data_record.items(): 
                                if (v!=old_record.get(k)) and (old_record.get(k) != master_old_record.get(k)):
                                    continue
                                updater[k] = v
                        tblobj.update(updater,old_record=old_record)
                    else:
                        tblobj.delete(data_record)
                elif event=='U':
                    tblobj.insert(data_record)   
                    
    def onPlugToForm(self,field):
        if self.db.currentPage.dbstore:
            return False
        return dict(lbl_color='red')
        
    def tableFkey(self,table):
        if isinstance(table,basestring):
            table = self.db.table(table)
        return '%s_%s' %(table.fullname.replace('.','_'),table.pkey)


    def getSubscriptionId(self,tblobj=None,pkey=None,dbstore=None):
        fkeyname = self.tableFkey(tblobj)
        f = self.query(where="""$tablename=:tablename AND 
                            $%s=:pkey AND 
                            $dbstore=:dbstore""" %fkeyname,
                            dbstore=dbstore,
                            tablename=tblobj.fullname,pkey=pkey).fetch()
        return f[0]['id'] if f else None
        



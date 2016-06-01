#!/usr/bin/env python
# encoding: utf-8
from gnr.app.gnrdbo import GnrDboTable, GnrDboPackage
from gnr.core.gnrbag import Bag
from gnr.core.gnrlang import instanceMixin
#from gnrpkg.multidb.multidbtable import MultidbTable
from gnr.sql.gnrsql import GnrSqlException
import os
import datetime


class Package(GnrDboPackage):
    def config_attributes(self):
        return dict(comment='multidb package',sqlschema='multidb',
                name_short='Multidb', name_long='Multidb', name_full='Multidb')

    def config_db(self, pkg):
        pass
    
    def copyTableToStore(self):
        pass

    def onApplicationInited(self):
        self.mixinMultidbMethods()

    def mixinMultidbMethods(self):
        db = self.application.db
        for pkg,pkgobj in db.packages.items():
            for tbl,tblobj in pkgobj.tables.items():
                if tblobj.dbtable.multidb:
                    instanceMixin(tblobj.dbtable, MultidbTable)


    def onBuildingDbobj(self):
        for pkgNode in self.db.model.src['packages']:
            for tblNode in pkgNode.value['tables']:
                multidb = tblNode.attr.get('multidb')
                tbl = tblNode.value
                if multidb is True:
                    self.multidb_configure(tbl,multidb)
                elif multidb is None:
                    multidb_fkeys = []
                    for col in tbl['columns']:
                        relattr = col.value.getAttr('relation')
                        if relattr and relattr.get('onDelete')=='cascade':
                            relatedColumn = relattr.get('related_column')
                            colpath = relatedColumn.split('.')
                            if len(colpath) == 2:
                                rel_pkg = pkgNode.label
                                rel_tblname, rel_colname = colpath
                            else:
                                rel_pkg, rel_tblname, rel_colname = colpath
                            rel_multidb = self.db.model.src.getNode('packages.%s.tables.%s' %(rel_pkg,rel_tblname)).attr.get('multidb')
                            if rel_multidb:
                                multidb_fkeys.append(col.label)
                    if multidb_fkeys:
                        tblNode.attr.update(multidb='parent',multidb_fkeys=','.join(multidb_fkeys))
                        tbl.column('__protected_by_mainstore',dtype='B',group='_')


    def multidb_configure(self,tbl,multidb):
        pkg = tbl.attributes['pkg']
        tblname = tbl.parentNode.label
        model = self.db.model
        subscriptiontbl =  model.src['packages.multidb.tables.subscription']
        pkey = tbl.parentNode.getAttr('pkey')
        pkeycolAttrs = tbl.column(pkey).getAttr()
        tblname = tbl.parentNode.label
        rel = '%s.%s.%s' % (pkg,tblname, pkey)
        fkey = rel.replace('.', '_')
        tbl.column('__multidb_default_subscribed',dtype='B',_pluggedBy='multidb.subscription',
                name_long='!!Subscribed by default',group='zz',_sysfield=True)
        tbl.formulaColumn('__multidb_subscribed',"""EXISTS (SELECT * 
                                                    FROM multidb.multidb_subscription AS sub
                                                    WHERE sub.dbstore = :env_target_store 
                                                          AND sub.tablename = '%s'
                                                    AND sub.%s = #THIS.%s
                                                    )""" %(tblname,fkey,pkey),dtype='B',
                                                    name_long='!!Subscribed',_sysfield=True,group='zz')
        subscriptiontbl.column(fkey, dtype=pkeycolAttrs.get('dtype'),_sysfield=True,
                              size=pkeycolAttrs.get('size'), group='zz').relation(rel, relation_name='subscriptions',external_relation=True,
                                                                                 many_group='zz', one_group='zz')

    def checkFullSyncTables(self,errorlog_folder=None,
                            dbstores=None,store_block=5,packages=None):
        if dbstores is None:
            dbstores = self.db.dbstores.keys()
        elif isinstance(dbstores,basestring):
            dbstores = dbstores.split(',')
        while dbstores:
            block = dbstores[0:store_block]
            dbstores = dbstores[store_block:]
            self.checkFullSyncTables_do(errorlog_folder=errorlog_folder,dbstores=block,packages=packages)
            print 'dbstore to do',len(dbstores)

    def checkFullSyncTables_do(self,errorlog_folder=None,dbstores=None,packages=None):
        errors = Bag()
        master_index = self.db.tablesMasterIndex()['_index_'] 
        for tbl in master_index.digest('#a.tbl'):
            pkg,tblname = tbl.split('.')
            if packages and not pkg in packages:
                continue
            tbl = self.db.table(tbl)
            multidb = tbl.multidb
            if not multidb or multidb=='one':
                continue
            if multidb=='*':
                print 'syncall',tbl.fullname
                main_f = tbl.query(addPkeyColumn=False,bagFields=True,
                                excludeLogicalDeleted=False,ignorePartition=True,
                                excludeDraft=False).fetch()
                tbl.checkSyncAll(dbstores=dbstores,main_fetch=main_f,errors=errors)
            else:
                print 'partial',tbl.fullname
                main_f = tbl.query(addPkeyColumn=False,bagFields=True,excludeLogicalDeleted=False).fetch()
                tbl.checkSyncPartial(dbstores=dbstores,main_fetch=main_f,errors=errors)
        if errorlog_folder:
            for dbstore,v in errors.items():
                p = '%s/%s.xml' %(errorlog_folder,dbstore)
                if v:
                    v.toXml(p,autocreate=True)
                else:
                    os.remove(p)

class Table(GnrDboTable):
    def use_dbstores(self,**kwargs):
        return False

class GnrMultidbException(GnrSqlException):
    """Standard Genro SQL Business Logic Exception
    
    * **code**: GNRSQL-101
    """
    code = 'GNRSQL-101'
    description = '!!%(description)s'
    caption = '!!%(msg)s'

class MultidbTable(object):
    def multidbExceptionClass(self):
        return GnrMultidbException

    def raw_insert(self, record, **kwargs):
        self.db.raw_insert(self, record,**kwargs)
        self.trigger_onInserted_multidb(record)

    def raw_update(self, record, old_record=None,**kwargs):
        self.trigger_onUpdating_multidb(record,old_record=old_record)
        self.db.raw_update(self, record,old_record=old_record,**kwargs)
        self.trigger_onUpdated_multidb(record,old_record=old_record)

    def raw_delete(self, record, **kwargs):
        self.trigger_onDeleting_multidb(record)
        self.db.raw_delete(self, record,**kwargs)

    def checkForeignKeys(self,record=None,old_record=None):
        for rel_table,rel_table_pkey,fkey in self.model.oneRelationsList(True):
            if old_record:
                checkKey = record.get(fkey)!=old_record.get(fkey) and record.get(fkey)
            else:
                checkKey = record.get(fkey)
            if checkKey:
                reltable = self.db.table(rel_table)
                if reltable.multidb is not True:
                    continue
                rec = reltable.query(where='$%s=:pk' %rel_table_pkey,pk=checkKey,limit=1).fetch()
                if rec and rec[0].get('__multidb_default_subscribed'):
                    continue
                storename = self.db.currentEnv['storename']
                with self.db.tempEnv(storename=self.db.rootstore):
                    reltable.multidbSubscribe(pkey=checkKey,dbstore=storename)

    def checkLocalUnify(self,record=None,old_record=None):
        if record.get(self.logicalDeletionField)\
            and not old_record.get(self.logicalDeletionField)\
            and record.get('__moved_related'):
                moved_related = Bag(record['__moved_related'])
                destPkey = moved_related['destPkey']
                destRecord = self.query(where='$%s=:dp' %self.pkey, 
                                          dp=destPkey).fetch()
                with self.db.tempEnv(connectionName='system'):
                    if destRecord:
                        destRecord = destRecord[0]
                    else:
                        storename = self.db.currentEnv['storename']
                        with self.db.tempEnv(storename=self.db.rootstore):
                            self.multidbSubscribe(pkey=destPkey,dbstore=storename)                        
                        f = self.query(where='$%s=:dp' %self.pkey, 
                                              dp=destPkey).fetch()
                        destRecord = f[0]
                    self.unifyRelatedRecords(sourceRecord=record,destRecord=destRecord,moved_relations=moved_related)

    def trigger_onInserting_multidb(self, record,old_record=None,**kwargs):
        if self.db.usingRootstore():
            return
        if not self.db.currentEnv.get('_multidbSync'):
            if self.multidb !='parent':
                raise GnrMultidbException(description='Multidb exception',msg="You cannot insert a record in a synced store %s" %self.fullname)
        else:
            if self.multidb=='parent':
                record['__protected_by_mainstore'] = True
            slaveEventHook = getattr(self,'onSlaveSyncing',None)
            if slaveEventHook:
                slaveEventHook(record,event='inserting')
            self.checkForeignKeys(record)

    def trigger_onUpdating_multidb(self, record,old_record=None,**kwargs):
        if self.db.usingRootstore():
            if old_record.get('__multidb_default_subscribed') != record.get('__multidb_default_subscribed'):
                self._onUpdating_master(record,old_record=old_record,**kwargs)
        else:
            self._onUpdating_slave(record,old_record=old_record)
            
    def _onUpdating_master(self, record,old_record=None,**kwargs):
        if record['__multidb_default_subscribed']:
            for f in self.relations_one.keys():
                if record.get(f):
                    relcol = self.column(f)
                    relatedTable = relcol.relatedTable().dbtable
                    if relatedTable.attributes.get('multidb_allRecords') or \
                      (not relcol.relatedColumnJoiner().get('foreignkey')):
                        continue
                    relatedTable.setColumns(record[f],__multidb_default_subscribed=True)
            self.db.table('multidb.subscription').syncChildren(self.fullname,record[self.pkey])
        else:
            raise GnrMultidbException(description='Multidb exception',msg="You cannot unset default subscription")

    def _onUpdating_slave(self, record,old_record=None,**kwargs):
        if self.db.currentEnv.get('_multidbSync'):
            slaveEventHook = getattr(self,'onSlaveSyncing',None)
            if slaveEventHook:
                slaveEventHook(record,old_record=old_record,event='updating')
            self.checkLocalUnify(record,old_record=old_record)
            self.checkForeignKeys(record,old_record=old_record)
        else:
            onLocalWrite = self.attributes.get('multidb_onLocalWrite') or 'raise'
            if onLocalWrite!='merge' and self.multidb!='parent':
                raise GnrMultidbException(description='Multidb exception',
                                            msg="You cannot update this record in a synced store")
    #def onSlaveSyncing(self,record=None,old_record=None,event=None):
    #    pass

    def trigger_onDeleting_multidb(self, record,**kwargs):      
        if self.db.usingRootstore():  
            self.onSubscriberTrigger(record,event='D')
        elif not self.db.currentEnv.get('_multidbSync'):
            pkey = record[self.pkey]
            if self.multidb == '*' or record.get('__multidb_default_subscribed'):
                raise GnrMultidbException(description='Multidb exception',msg="You cannot delete this record from a synced store")
            elif self.multidb == 'parent':
                __protected_by_mainstore = record['__protected_by_mainstore'] if '__protected_by_mainstore' in record \
                                          else self.readColumns(pkey=record[self.pkey],columns='__protected_by_mainstore')
                if __protected_by_mainstore:
                    raise GnrMultidbException(description='Multidb exception',msg="Protected by mainstore")
            elif self.multidb is True :
                tblsub = self.db.table('multidb.subscription')
                subscription_id = tblsub.getSubscriptionId(tblobj=self,dbstore=self.db.currentEnv.get('storename'),pkey=pkey)
                if subscription_id:
                    tblsub.raw_delete(dict(id=subscription_id)) # in order to avoid subscription delete trigger

    def trigger_onInserted_multidb(self, record,**kwargs):
        if self.db.usingRootstore():  
            self.onSubscriberTrigger(record,event='I')

    def trigger_onUpdated_multidb(self, record,old_record=None,**kwargs):
        if self.db.usingRootstore():  
            self.onSubscriberTrigger(record,old_record=old_record,event='U')

    def onLoading_multidb(self,record,newrecord,loadingParameters,recInfo):
        if not self.db.usingRootstore():
            if self.attributes.get('multidb_onLocalWrite') == 'merge':
                changelist = self.db.table('multidb.subscription').decoreMergedRecord(self,record)
                recInfo['_multidb_diff'] = changelist
                if changelist or recInfo.get('ignoreReadOnly'):
                    return
            recInfo['_protect_write'] = True
            recInfo['_protect_write_message'] = "!!Can be changed only in main store"

    def checkSyncPartial(self,dbstores=None,main_fetch=None,errors=None):
        queryargs = dict(addPkeyColumn=False,bagFields=True,excludeLogicalDeleted=False,
                        ignorePartition=True,excludeDraft=False)
        checkdict = dict([(r[self.pkey],dict(r)) for r in main_fetch])
        substable = self.db.table('multidb.subscription')
        fkeyname = substable.tableFkey(self)
        subscriptions = substable.query(where='$tablename=:t',t=self.fullname).fetchGrouped('dbstore')
        for dbstore in dbstores:
            store_subs = dict([(s[fkeyname],s['id'])for s in subscriptions.pop(dbstore,[])])
            with self.db.tempEnv(storename=dbstore):
                store_f = self.query(**queryargs).fetch()
                for r in store_f:
                    record_pkey = r[self.pkey]
                    main_r = checkdict.get(record_pkey)
                    if not main_r:
                        if not self.hasRelations(r):
                            self.raw_delete(r)
                        else:
                            errors.setItem('%s.%s.storeonly.%s' %(dbstore,self.fullname,record_pkey),True)
                        continue
                    sub_id = store_subs.pop(record_pkey,None)
                    default_subscribed = main_r.get('__multidb_default_subscribed')
                    if default_subscribed:
                        if sub_id:
                            substable.raw_delete(dict(id=sub_id))
                    elif not sub_id:
                        if not self.hasRelations(r):
                            self.raw_delete(r)
                            continue
                        else:
                            subrec = {'tablename':self.fullname,
                                    fkeyname:r[self.pkey],
                                    'dbstore':dbstore,
                                    'id':substable.newPkeyValue()}
                            substable.trigger_setTSNow(subrec,'__ins_ts')
                            substable.raw_insert(subrec)
                    elif not self.hasRelations(r):
                        self.raw_delete(r)
                        substable.raw_delete(dict(id=sub_id))
                    diff = substable.getRecordDiff(main_r,r)
                    to_update = False
                    localdiff = dict()
                    for field,values in diff.items():
                        main_value,store_value = values
                        if main_value is not None:
                            print '\t\t setting',field,main_value,'instead of',store_value
                            r[field] = main_value
                            to_update = True
                        elif r[field] is not None:
                            localdiff[field] = store_value
                    if localdiff:
                        errors.setItem('%s.%s.different_storevalue.%s' %(dbstore,self.fullname,record_pkey),True,**localdiff)
                    if to_update:
                        self.raw_update(r)
                self.db.commit()
            self.db.commit()

    def _checkSyncAll_store(self,main_fetch=None,insertManyData=None,
                            queryargs=None,pkeyfield=None,ts=None,
                            errors=None,dbstore=None):
        if not insertManyData:
            self.empty()
            return
        checkdict = dict([(r[pkeyfield],dict(r)) for r in main_fetch])
        store_f = self.query(**queryargs).fetch()
        if not store_f and insertManyData:
            self.insertMany(insertManyData)
            return
        diffrec = list()
        for r in store_f:
            r = dict(r)
            record_pkey = r[pkeyfield]
            main_r = checkdict.pop(record_pkey,None)
            if not main_r:
                if not self.hasRelations(r):
                    self.raw_delete(r)
                else:
                    errors.setItem('%s.%s.wrong_allsync_record.%s' %(dbstore,self.fullname,record_pkey),True)
                    if self.logicalDeletionField:
                        r[self.logicalDeletionField] = ts
                        self.raw_update(r)
                return
            checkdiff = [(k,v,main_r[k]) for k,v in r.items() if k not in ('__ins_ts','__mod_ts','__version','__del_ts','__moved_related') if v!=main_r[k]]
            if checkdiff:
                diffrec.append((main_r,r))
                
        if diffrec or checkdict:
            try:
                self.empty()
                self.insertMany(insertManyData)
            except Exception:
                for r,oldr in diffrec:
                    self.raw_update(r,oldr)
                for main_r in checkdict.values():
                    self.raw_insert(main_r)

    def checkSyncAll(self,dbstores=None,main_fetch=None,errors=None):
        pkeyfield = self.pkey
        insertManyData = [dict(r) for r in main_fetch]
        ts = datetime.datetime.now()
        queryargs = dict(addPkeyColumn=False,bagFields=True,excludeLogicalDeleted=False,ignorePartition=True,excludeDraft=False)
        for dbstore in dbstores:
            with self.db.tempEnv(storename=dbstore):
                self._checkSyncAll_store(main_fetch=main_fetch,insertManyData=insertManyData,
                                         queryargs=queryargs, pkeyfield=pkeyfield, 
                                         ts=ts,errors=errors,dbstore=dbstore)
                self.db.commit()
            self.db.commit()

    def onSubscriberTrigger(self,record,old_record=None,event=None):
        subscribedStores = self.getSubscribedStores(record=record)
        mergeUpdate = self.attributes.get('multidb_onLocalWrite')=='merge' or self.multidb=='parent'
        pkey = record[self.pkey]
        tblsub = self.db.table('multidb.subscription')
        for storename in subscribedStores:
            tblsub.syncStore(event=event,storename=storename,tblobj=self,pkey=pkey,
                            master_record=record,master_old_record=old_record,mergeUpdate=mergeUpdate)
  
    def getSubscribedStores(self,record):
        multidb = self.multidb
        if multidb=='one':
            store = self.multidb_getForcedStore(record)
            return [store] if store else []
        elif self.multidb == '*' or record.get('__multidb_default_subscribed'):
            return self.db.dbstores.keys()
        elif multidb is True:
            tablename = self.fullname
            tblsub = self.db.table('multidb.subscription')
            fkeyname = tblsub.tableFkey(self)
            pkey = record[self.pkey]
            subscribedStores = tblsub.query(where='$tablename=:tablename AND $%s=:pkey' %fkeyname,
                                    columns='$dbstore',addPkeyColumn=False,
                                    tablename=tablename,pkey=pkey,distinct=True).fetch()                
            return [s['dbstore'] for s in subscribedStores]
        else:
            subscribedStores = set(self.db.dbstores.keys())
            do_sync = False
            multidb_fkeys = self.attributes['multidb_fkeys']
            for fkey in multidb_fkeys.split(','):
                if record.get(fkey):
                    do_sync = True
                relatedTable = self.column(fkey).relatedTable().dbtable
                multidb = relatedTable.multidb
                if multidb is True and record.get(fkey):
                    parentRecord = relatedTable.record(pkey=record.get(fkey)).output('dict')
                    parentSubscribedStores = set(relatedTable.getSubscribedStores(parentRecord))
                    subscribedStores = subscribedStores.intersection(parentSubscribedStores)
            return list(subscribedStores) if do_sync else []

    def multidbSubscribe(self,pkey,dbstore=None):
        self.db.table('multidb.subscription').addSubscription(table=self.fullname,pkey=pkey,dbstore=dbstore)
           

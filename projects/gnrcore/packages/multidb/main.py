#!/usr/bin/env python
# encoding: utf-8
from __future__ import print_function
from past.builtins import basestring
from builtins import object
from gnr.app.gnrdbo import GnrDboTable, GnrDboPackage
from gnr.core.gnrdecorator import metadata
from gnr.core.gnrbag import Bag
from gnr.core.gnrlang import instanceMixin
#from gnrpkg.multidb.multidbtable import MultidbTable
from gnr.sql.gnrsql import GnrSqlException
import os
import datetime

FIELD_BLACKLIST = ('__ins_ts','__mod_ts','__version','__del_ts','__moved_related')

class Package(GnrDboPackage):
    def config_attributes(self):
        return dict(comment='multidb package',sqlschema='multidb',
                name_short='Multidb', name_long='Multidb', name_full='Multidb')

    def config_db(self, pkg):
        pass
    
    def copyTableToStore(self):
        pass

    def getStorePreference(self):
        if not self.attributes.get('storetable'):
            return Bag()
        storename = self.db.currentEnv.get('storename')
        store_record = self.db.table(self.attributes['storetable']).record(dbstore=storename).output('record')
        return store_record['preferences'] or Bag()

    def setStorePreference(self,pkg=None,value=None):
        storename = self.db.currentEnv.get('storename')
        with self.db.tempEnv(connectionName='system',storename=self.db.rootstore):
            with self.db.table(self.attributes['storetable']).recordToUpdate(dbstore=storename) as rec:
                rec['preferences'][pkg] = value
            self.db.commit()

    def onApplicationInited(self):
        self.mixinMultidbMethods()

    def mixinMultidbMethods(self):
        db = self.application.db
        for pkg,pkgobj in db.packages.items():
            for tbl,tblobj in pkgobj.tables.items():
                if tblobj.dbtable.multidb:
                    instanceMixin(tblobj.dbtable, MultidbTable)


    def _getParentMultidb(self,pkgId,tblNode):
        multidb_fkeys = tblNode.attr.get('multidb_fkeys')
        if multidb_fkeys:
            return multidb_fkeys
        else:
            multidb_fkeys = []
        for col in tblNode.value['columns']:
            relattr = col.value.getAttr('relation')
            if relattr and relattr.get('onDelete')=='cascade':
                relatedColumn = relattr.get('related_column')
                colpath = relatedColumn.split('.')
                if len(colpath) == 2:
                    rel_pkg = pkgId
                    rel_tblname, rel_colname = colpath
                else:
                    rel_pkg, rel_tblname, rel_colname = colpath
                rel_multidb = self.db.model.src.getNode('packages.%s.tables.%s' %(rel_pkg,rel_tblname)).attr.get('multidb')
                if rel_multidb and rel_multidb!='one':
                    multidb_fkeys.append(col.label)
        return ','.join(multidb_fkeys)

    def onBuildingDbobj(self):
        for pkgNode in self.db.model.src['packages']:
            if not pkgNode.value:
                continue
            for tblNode in pkgNode.value['tables']:
                multidb = tblNode.attr.get('multidb')
                tbl = tblNode.value
                if multidb is True:
                    self.multidb_configure(tbl,multidb)
                elif multidb is None:
                    multidb_fkeys =  self._getParentMultidb(pkgNode.label,tblNode)
                    if multidb_fkeys:
                        multidb_onLocalWrite=tblNode.attr.get('multidb_onLocalWrite') or 'merge'
                        tblNode.attr.update(multidb='parent',multidb_onLocalWrite=multidb_onLocalWrite,multidb_fkeys=multidb_fkeys)
                        tbl.column('__protected_by_mainstore',dtype='B',group='zz',protectedFields=True)


    def multidb_configure(self,tbl,multidb):
        pkg = tbl.attributes['pkg']
        model = self.db.model
        subscriptiontbl =  model.src['packages.multidb.tables.subscription']
        pkey = tbl.parentNode.getAttr('pkey')
        pkeycolAttrs = tbl.column(pkey).getAttr()
        tblname = tbl.parentNode.label
        rel = '%s.%s.%s' % (pkg,tblname, pkey)
        fkey = rel.replace('.', '_')
        tbl.column('__multidb_default_subscribed',dtype='B',_pluggedBy='multidb.subscription',
                name_long='!!Subscribed by default',group='zz',_sysfield=True)
        tbl.formulaColumn('__multidb_subscribed',
                            exists=dict(table='multidb.subscription',
                                        where='$tablename=:tname AND $dbstore = :env_target_store AND $%s = #THIS.%s' %(fkey,pkey),
                                        tname='%s.%s' %(pkg,tblname)),dtype='B',
                            name_long='!!Subscribed',_sysfield=True,group='zz')
        subscriptiontbl.column(fkey, dtype=pkeycolAttrs.get('dtype'),_sysfield=True,
                              size=pkeycolAttrs.get('size'), group='zz').relation(rel, relation_name='subscriptions',external_relation=True,
                                                                                 many_group='zz', one_group='zz')

    def checkFullSyncTables(self,errorlog_folder=None,
                            dbstores=None,store_block=5,packages=None,tbllist=None):
        if dbstores is None:
            dbstores = list(self.db.dbstores.keys())
        elif isinstance(dbstores,basestring):
            dbstores = dbstores.split(',')
        while dbstores:
            block = dbstores[0:store_block]
            dbstores = dbstores[store_block:]
            self.checkFullSyncTables_do(errorlog_folder=errorlog_folder,dbstores=block,packages=packages,tbllist=tbllist)
            print('dbstore to do',len(dbstores))

    def checkFullSyncTables_do(self,errorlog_folder=None,dbstores=None,packages=None,tbllist=None):
        errors = Bag()
        master_index = self.db.tablesMasterIndex(filterPackages=packages)['_index_'] 
        for tbl in master_index.digest('#a.tbl'):
            if tbllist and tbl not in tbllist:
                continue
            pkg,tblname = tbl.split('.')
            if packages and pkg not in packages:
                continue
            tbl = self.db.table(tbl)
            multidb = tbl.multidb
            if not multidb or multidb=='one' or multidb=='parent':
                continue
            main_f = tbl.query(addPkeyColumn=False,bagFields=True,
                                excludeLogicalDeleted=False,ignorePartition=True,
                                excludeDraft=False).fetch()
            if multidb=='*':
                tbl.checkSyncAll(dbstores=dbstores,main_fetch=main_f,errors=errors)
            else:
                tbl.checkSyncPartial(dbstores=dbstores,main_fetch=main_f,errors=errors)

        if errorlog_folder:
            for dbstore,v in list(errors.items()):
                p = '%s/%s.xml' %(errorlog_folder,dbstore)
                if v:
                    v.toXml(p,autocreate=True)
                else:
                    os.remove(p)


    def onAuthentication(self,avatar):
        """dbstore user check"""
        dbstorepage = self.db.application.site.currentPage.dbstore
        if avatar.user_record['dbstore'] and dbstorepage!=avatar.user_record['dbstore']:
            avatar.user_tags = ''

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
        do_multidb_trigger = not self.db.currentEnv.get('avoid_trigger_multidb')
        if do_multidb_trigger:
            self.trigger_onInserting_multidb(record)
        self.db.raw_insert(self, record,**kwargs)
        if do_multidb_trigger:
            self.trigger_onInserted_multidb(record)

    def raw_update(self, record, old_record=None,**kwargs):
        do_multidb_trigger = not self.db.currentEnv.get('avoid_trigger_multidb')
        if do_multidb_trigger:
            self.trigger_onUpdating_multidb(record,old_record=old_record)
        kwargs.setdefault('pkey',old_record.get(self.pkey))
        self.db.raw_update(self, record,old_record=old_record,**kwargs)
        if do_multidb_trigger:
            self.trigger_onUpdated_multidb(record,old_record=old_record)

    def raw_delete(self, record, **kwargs):
        if not self.db.currentEnv.get('avoid_trigger_multidb'):
            self.trigger_onDeleting_multidb(record)
        self.db.raw_delete(self, record,**kwargs)


    def unifyRecords(self,sourcePkey=None,destPkey=None):
        if self.db.usingRootstore():
            sourceRecord = self.record(pkey=sourcePkey,for_update=True).output('dict')
            destRecord = self.record(pkey=destPkey,for_update=True).output('dict')
            with self.db.tempEnv(avoid_trigger_multidb='*'):
                self._unifyRecords_default(sourceRecord,destRecord)
            sourceRecord_stores = set(self.getSubscribedStores(sourceRecord))
            destRecord_stores = set(self.getSubscribedStores(destRecord))
            stores_to_check =  destRecord_stores.union(sourceRecord_stores)
            common_stores = destRecord_stores.intersection(sourceRecord_stores)

            for store in stores_to_check:
                with self.db.tempEnv(storename=store,_multidbSync=True):
                    print('in store',store)
                    if store in common_stores:
                        sr = self.record(pkey=sourcePkey,for_update=True).output('dict')
                        dr = self.record(pkey=destPkey,for_update=True).output('dict')
                        print('unifiy in ',store)
                        self._unifyRecords_default(sr,dr)
                    elif store in sourceRecord_stores:
                        with self.db.tempEnv(storename=self.db.rootstore):
                            self.multidbSubscribe(pkey=destPkey,dbstore=store)
                        sr = self.record(pkey=sourcePkey,for_update=True).output('dict')
                        dr = self.record(pkey=destPkey,for_update=True).output('dict')
                        self._unifyRecords_default(sr,dr)

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
            for f in list(self.relations_one.keys()):
                if record.get(f):
                    relcol = self.column(f)
                    relatedTable = relcol.relatedTable().dbtable
                    if relatedTable.multidb=='*' or relatedTable.attributes.get('multidb_allRecords') or \
                      (not relcol.relatedColumnJoiner().get('foreignkey')):
                        continue
                    relatedTable.setColumns(record[f],__multidb_default_subscribed=True)
            self.syncChildren(record[self.pkey])
        else:
            raise GnrMultidbException(description='Multidb exception',msg="You cannot unset default subscription")

    def _onUpdating_slave(self, record,old_record=None,**kwargs):
        if self.db.currentEnv.get('_multidbSync'):
            slaveEventHook = getattr(self,'onSlaveSyncing',None)
            if slaveEventHook:
                slaveEventHook(record,old_record=old_record,event='updating')
            #print 'before checkLocalUnify'
            #self.checkLocalUnify(record,old_record=old_record) #REMOVED UNIFY CUSTOM FOR MULTDB MAKE IT USELESS
            self.checkForeignKeys(record,old_record=old_record)
        else:
            onLocalWrite = self.attributes.get('multidb_onLocalWrite') or 'raise'
            if onLocalWrite!='merge':
                raise GnrMultidbException(description='Multidb exception',
                                            msg="You cannot update this record in a synced store %s" %self.fullname)
    #def onSlaveSyncing(self,record=None,old_record=None,event=None):
    #    pass

    def trigger_onDeleting_multidb(self, record,**kwargs):      
        if self.db.usingRootstore():  
            self.onSubscriberTrigger(record,event='D')
        elif not self.db.currentEnv.get('_multidbSync'):
            pkey = record[self.pkey]
            if self.multidb == '*' or record.get('__multidb_default_subscribed'):
                raise GnrMultidbException(description='Multidb exception',msg="You cannot delete this record from a synced store")
            elif self.multidb == 'parent' :
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
        elif self.multidb=='parent' and self.db.currentEnv.get('_parentSyncChildren'):
            with self.db.tempEnv(storename=self.db.rootstore):
                self.syncChildren(record[self.pkey])

    def trigger_onUpdated_multidb(self, record,old_record=None,**kwargs):
        if self.db.usingRootstore():  
            self.onSubscriberTrigger(record,old_record=old_record,event='U')

    def onLoading_multidb(self,record,newrecord,loadingParameters,recInfo):
        if loadingParameters.get('_eager_record_stack') or newrecord:
            return
        if not self.db.usingRootstore():
            if self.attributes.get('multidb_onLocalWrite') == 'merge':
                changelist = self.decoreMergedRecord(record)
                recInfo['_multidb_diff'] = changelist
                if changelist or recInfo.get('ignoreReadOnly'):
                    return
            recInfo['_protect_write'] = True
            recInfo['_protect_write_message'] = "!!Can be changed only in main store"


    def syncChildren(self,pkey):
        with self.db.tempEnv(_parentSyncChildren=True):
            #many_rels = [manyrel.split('.') for manyrel, onDelete in self.relations_many.digest('#a.many_relation,#a.onDelete') if onDelete=='cascade']
            for many_rel in self.relations_many.digest('#a.many_relation'):
                pkg,tbl,fkey = many_rel.split('.')
                childtable = self.db.table('%s.%s' %(pkg,tbl))
                if not childtable.multidb=='parent':
                    continue
                multidb_fkeys = childtable.attributes.get('multidb_fkeys').split(',')
                if fkey in multidb_fkeys:
                    childtable.touchRecords(where='$%s=:pk' %fkey,pk=pkey)

    def checkSyncPartial(self,dbstores=None,main_fetch=None,errors=None):
        queryargs = dict(addPkeyColumn=False,bagFields=True,excludeLogicalDeleted=False,
                        ignorePartition=True,excludeDraft=False)
        checkdict = dict([(r[self.pkey],dict(r)) for r in main_fetch])
        substable = self.db.table('multidb.subscription')
        fkeyname = substable.tableFkey(self)
        subscriptions = substable.query(where='$tablename=:t',t=self.fullname).fetchGrouped('dbstore')
        for dbstore in dbstores:
            store_subs = dict([(s[fkeyname],s['id'])for s in subscriptions.pop(dbstore,[])])
            with self.db.tempEnv(storename=dbstore,_multidbSync=True):
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
                    diff = self.getRecordDiff(main_r,r)
                    to_update = False
                    localdiff = dict()
                    for field,values in list(diff.items()):
                        main_value,store_value = values
                        if main_value is not None:
                            print('\t\t setting',field,main_value,'instead of',store_value)
                            r[field] = main_value
                            to_update = True
                        elif r[field] is not None:
                            localdiff[field] = store_value
                    if localdiff:
                        errors.setItem('%s.%s.different_storevalue.%s' %(dbstore,self.fullname,record_pkey),True,**localdiff)
                    if to_update:
                        self.raw_update(r)
                    self._checkSyncChildren(main_r[self.pkey])
                self.db.commit()
            self.db.commit()

    def _checkSyncChildren(self,pkey):
        for many_rel in self.relations_many.digest('#a.many_relation'):
            pkg,tbl,fkey = many_rel.split('.')
            childtable = self.db.table('%s.%s' %(pkg,tbl))
            if not childtable.multidb=='parent':
                continue
            multidb_fkeys = childtable.attributes.get('multidb_fkeys').split(',')
            if fkey in multidb_fkeys:
                main_children_records = childtable.query(where='$%s=:pk' %fkey,pk=pkey,addPkeyColumn=False,bagFields=True,excludeLogicalDeleted=False,
                                                    ignorePartition=True,excludeDraft=False,_storename=False).fetch()
                store_children_records = childtable.query(where='$%s=:pk' %fkey,pk=pkey,addPkeyColumn=False,bagFields=True,excludeLogicalDeleted=False,
                                                    ignorePartition=True,excludeDraft=False).fetchAsDict(childtable.pkey)
                for r in main_children_records:
                    sr = store_children_records.get(r[childtable.pkey])
                    cr = dict(r)
                    cr['__protected_by_mainstore'] = True
                    if not sr:
                        childtable.raw_insert(cr)
                    else:
                        childtable.raw_update(cr,sr)
                    childtable._checkSyncChildren(cr['id'])


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
                        old_r = dict(r)
                        r[self.logicalDeletionField] = ts
                        self.raw_update(r,old_r)
                continue
            checkdiff = [(k,v,main_r[k]) for k,v in list(r.items()) if k not in ('__ins_ts','__mod_ts','__version','__del_ts','__moved_related') if v!=main_r[k]]
            if checkdiff:
                diffrec.append((main_r,r))
            self._checkSyncChildren(main_r[pkeyfield])
        if diffrec or checkdict:
            try:
                self.empty()
                self.insertMany(insertManyData)
            except Exception:
                for r,oldr in diffrec:
                    self.raw_update(r,oldr)
                for main_r in list(checkdict.values()):
                    self.raw_insert(main_r)


    def checkSyncAll(self,dbstores=None,main_fetch=None,errors=None):
        pkeyfield = self.pkey
        insertManyData = [dict(r) for r in main_fetch]
        ts = datetime.datetime.now()
        queryargs = dict(addPkeyColumn=False,bagFields=True,excludeLogicalDeleted=False,ignorePartition=True,excludeDraft=False)
        for dbstore in dbstores:
            with self.db.tempEnv(storename=dbstore,_multidbSync=True):
                self._checkSyncAll_store(main_fetch=main_fetch,insertManyData=insertManyData,
                                         queryargs=queryargs, pkeyfield=pkeyfield, 
                                         ts=ts,errors=errors,dbstore=dbstore)
                self.db.commit()
            self.db.commit()

    def onSubscriberTrigger(self,record,old_record=None,event=None):
        subscribedStores = self.getSubscribedStores(record=record)
        mergeUpdate = self.attributes.get('multidb_onLocalWrite')=='merge'
        pkey = old_record[self.pkey] if old_record else record[self.pkey]
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
            return list(self.db.dbstores.keys())
        elif multidb is True:
            tablename = self.fullname
            tblsub = self.db.table('multidb.subscription')
            fkeyname = tblsub.tableFkey(self)
            pkey = record[self.pkey]
            subscribedStores = tblsub.query(where='$tablename=:tablename AND $%s=:pkey AND $dbstore IN :allstores' %fkeyname,
                                    columns='$dbstore',addPkeyColumn=False,allstores=self.db.dbstores.keys(),
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
                if multidb and record.get(fkey):
                    parentRecord = relatedTable.record(pkey=record.get(fkey)).output('dict')
                    parentSubscribedStores = set(relatedTable.getSubscribedStores(parentRecord))
                    subscribedStores = subscribedStores.intersection(parentSubscribedStores)
            return list(subscribedStores) if do_sync else []
    

    def multidbSubscribe(self,pkey,dbstore=None):
        self.db.table('multidb.subscription').addSubscription(table=self.fullname,pkey=pkey,dbstore=dbstore)


    def decoreMergedRecord(self,record):
        main_record = self.record(pkey=record[self.pkey],
                                _storename=False).output('record')
        changelist = []
        for k,v in list(main_record.items()):
            if k not in FIELD_BLACKLIST:
                if record[k] != v:
                    changelist.append(k)
                    record.setAttr(k,wdg__class='multidb_local_change',multidb_mainvalue=v)
        return ','.join(changelist)


    def getRecordDiff(self,main_record,store_record):
        result = dict()
        for k,v in list(main_record.items()):
            if k not in FIELD_BLACKLIST:
                if store_record[k] != v:
                    result[k] = (v,store_record[k])
        return result

    def createSysRecords(self,do_update=None):
        if not self.db.usingRootstore():
            return
        syscodes = []
        for m in dir(self):
            if m.startswith('sysRecord_') and m!='sysRecord_':
                method = getattr(self,m)
                if getattr(method,'mandatory',False):
                    syscodes.append(m[10:])
        commit = False
        if syscodes:
            f = self.query(where='$__syscode IN :codes',codes=syscodes).fetchAsDict('__syscode')
            for syscode in syscodes:
                if syscode not in f:
                    self.sysRecord(syscode)
                    commit = True
        if commit:
            self.db.commit()

    def sysRecord(self,syscode):
        if not self.db.usingRootstore():
            with self.db.tempEnv(storename=self.db.rootstore):
                return self.sysRecord(syscode)

        def createCb(key):
            extra_fields = dict()
            if not self.multidb=='*':
                extra_fields['__multidb_default_subscribed'] = True
            return self._sysRecordCreateCb(key,**extra_fields)
        return self.cachedRecord(syscode,keyField='__syscode',createCb=createCb)

#!/usr/bin/env python
# encoding: utf-8
from gnr.app.gnrdbo import GnrDboTable, GnrDboPackage
from gnr.core.gnrlang import instanceMixin
from gnr.core.gnrbag import Bag
import os

class MultidbTable(object):

    def raw_insert(self, record, **kwargs):
        self.db.raw_insert(self, record,**kwargs)
        self.trigger_multidbSyncInserted(record)

    def raw_update(self, record, old_record=None,**kwargs):
        self.trigger_multidbSyncUpdating(record,old_record=old_record)
        self.db.raw_update(self, record,old_record=old_record,**kwargs)
        self.trigger_multidbSyncUpdated(record,old_record=old_record)

    def raw_delete(self, record, **kwargs):
        self.trigger_multidbSyncDeleting(record)
        self.db.raw_delete(self, record,**kwargs)

    def trigger_multidbSyncUpdating(self, record,old_record=None,**kwargs):
        multidb_subscription = self.db.table('multidb.subscription')
        if self.db.usingRootstore():
            if old_record.get('__multidb_default_subscribed') != record.get('__multidb_default_subscribed'):
                if record['__multidb_default_subscribed']:
                    for f in self.relations_one.keys():
                        if record.get(f):
                            relcol = self.column(f)
                            relatedTable = relcol.relatedTable().dbtable
                            if relatedTable.attributes.get('multidb_allRecords') or \
                              (not relcol.relatedColumnJoiner().get('foreignkey')):
                                continue
                            relatedTable.setColumns(record[f],__multidb_default_subscribed=True)
                else:
                    raise multidb_subscription.multidbExceptionClass()(description='Multidb exception',msg="You cannot unset default subscription")
        else:
            slaveEventHook = getattr(self,'onSlaveSyncing',None)
            if slaveEventHook:
                slaveEventHook(record,old_record=old_record,event='updating')
            multidb_subscription.onSlaveUpdating(self,record,old_record=old_record)
            
    def trigger_multidbSyncInserting(self, record,old_record=None,**kwargs):
        if not self.db.usingRootstore():
            slaveEventHook = getattr(self,'onSlaveSyncing',None)
            if slaveEventHook:
                slaveEventHook(record,event='inserting')
            self.db.table('multidb.subscription').checkForeignKeys(self,record)

    def trigger_multidbSyncUpdated(self, record,old_record=None,**kwargs):
        self.db.table('multidb.subscription').onSubscriberTrigger(self,record,old_record=old_record,event='U')
     
    def trigger_multidbSyncInserted(self, record,**kwargs):
        self.db.table('multidb.subscription').onSubscriberTrigger(self,record,event='I')
    
    def trigger_multidbSyncDeleting(self, record,**kwargs):        
        self.db.table('multidb.subscription').onSubscriberTrigger(self,record,event='D')
     
                                                             

    def onLoading_multidb(self,record,newrecord,loadingParameters,recInfo):
        if not self.db.usingRootstore():
            if self.attributes.get('multidb_onLocalWrite') == 'merge':
                changelist = self.db.table('multidb.subscription').decoreMergedRecord(self,record)
                recInfo['_multidb_diff'] = changelist
                if changelist or recInfo.get('ignoreReadOnly'):
                    return
            recInfo['_protect_write'] = True
            recInfo['_protect_write_message'] = "!!Can be changed only in main store"




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
                if hasattr(tblobj.dbtable,'use_dbstores') and tblobj.dbtable.use_dbstores():
                    instanceMixin(tblobj.dbtable, MultidbTable)


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
        master_index = self.db.tablesMasterIndex()['_index_'] #lambda tblobj: tblobj.dbtable.isMultidbTable() or tblobj.fullname=='hosting.slot')
        for tbl in master_index.digest('#a.tbl'):
            pkg,tblname = tbl.split('.')
            if packages and not pkg in packages:
                continue
            tbl = self.db.table(tbl)
            if not tbl.isMultidbTable():
                continue
            if tbl.attributes.get('multidb_forcedStore'):
                continue
            if tbl.attributes.get('multidb_allRecords') is True:
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

#!/usr/bin/env python
# encoding: utf-8
from gnr.app.gnrdbo import GnrDboTable, GnrDboPackage
from gnr.core.gnrlang import instanceMixin
from gnr.core.gnrbag import Bag

class MultidbTable(object):
    def onLoading_multidb(self,record,newrecord,loadingParameters,recInfo):
        if not self.db.usingRootstore():
            if self.attributes.get('multidb_onLocalWrite') == 'merge':
                changelist = self.db.table('multidb.subscription').decoreMergedRecord(self,record)
                recInfo['_multidb_diff'] = changelist
                if changelist or recInfo.get('ignoreReadOnly'):
                    return
            recInfo['_protect_write'] = True
            recInfo['_protect_write_message'] = "!!Can be changed only in main store"
       #currentEnv = self.db.currentEnv
       #if currentEnv.get('storename') and self.use_dbstores():
       #    pass
       #print x



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
                    instanceMixin(tblobj.dbtable, MultidbTable, methods='onLoading_multidb', suffix='multidb')


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
        syncall = []
        partial = []
        packages = packages or self.db.packages.keys()
        for pkg in packages:
            pkgobj = self.db.packages[pkg]
            for tableobj in pkgobj.tables.values():
                tbl = tableobj.dbtable
                if not tbl.isMultidbTable():
                    continue
                if tbl.attributes.get('multidb_forcedStore'):
                    continue
                if tbl.attributes.get('multidb_allRecords') is True:
                    syncall.append(tbl)
                else:
                    partial.append(tbl)
        
        print 'syncall start'
        for tbl in syncall:
            print '\t',tbl.fullname
            main_f = tbl.query(addPkeyColumn=False,bagFields=True,excludeLogicalDeleted=False).fetch()
            tbl.checkSyncAll(dbstores=dbstores,main_fetch=main_f,errors=errors)
        print 'syncall done'
        print 'partial start'
        for tbl in partial:
            print '\t',tbl.fullname
            main_f = tbl.query(addPkeyColumn=False,bagFields=True,excludeLogicalDeleted=False).fetch()
            tbl.checkSyncPartial(dbstores=dbstores,main_fetch=main_f,errors=errors)
        print 'partial done'
        if errors and errorlog_folder:
            for dbstore,v in errors.items():
                v.toXml('%s/%s.xml' %(errorlog_folder,dbstore),autocreate=True)



                    

class Table(GnrDboTable):
    def use_dbstores(self,**kwargs):
        return False

#!/usr/bin/env python
# encoding: utf-8
from gnr.app.gnrdbo import GnrDboTable, GnrDboPackage
from gnr.core.gnrlang import instanceMixin

class MultidbTable(object):
    def onLoading_multidb(self,record,newrecord,loadingParameters,recInfo):
        if not self.db.usingRootstore():
            if self.attributes.get('multidb_onLocalWrite') == 'merge':
                changed = self.db.table('multidb.subscription').decoreMergedRecord(self,record)
                print 'changed',changed
                if changed or recInfo.get('ignoreReadOnly'):
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


    def checkFullSyncTables(self,dbstores=None):
        if dbstores is None:
            dbstores = self.db.dbstores.keys()
        elif isinstance(dbstores,basestring):
            dbstores = dbstores.split(',')
        print 'dbstores',dbstores
        for pkgobj in self.db.packages.values():
            for tableobj in pkgobj.tables.values():
                tblattr = tableobj.attributes
                if tblattr.get('multidb_allRecords') is True:
                    print 'check for table',tableobj.fullname
                    print '\t check for store',tableobj.fullname
                    tableobj.dbtable.checkSyncAll(dbstores=dbstores)


                    

class Table(GnrDboTable):
    def use_dbstores(self,**kwargs):
        return False

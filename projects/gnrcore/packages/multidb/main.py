#!/usr/bin/env python
# encoding: utf-8
from gnr.app.gnrdbo import GnrDboTable, GnrDboPackage

class Package(GnrDboPackage):
    def config_attributes(self):
        return dict(comment='multidb package',sqlschema='multidb',
                name_short='Multidb', name_long='Multidb', name_full='Multidb')

    def config_db(self, pkg):
        pass
    
    def copyTableToStore(self):
        pass

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

#!/usr/bin/env python
# encoding: utf-8
from gnr.app.gnrdbo import GnrDboTable, GnrDboPackage

class Package(GnrDboPackage):
    def config_attributes(self):
        return dict(sqlschema='sys',
                    comment='sys',
                    name_short='System',
                    name_long='System',
                    name_full='System',_syspackage=True)
                    
    def config_db(self,pkg):
        #you can describe here your database or separate table into classes
        pass
    def newUserUrl(self):
        return 'adm/new_user'

    def modifyUserUrl(self):
        return 'adm/modify_user'

    def loginUrl(self):
        return 'common/_adm/login'

    def onApplicationInited(self):
        pass
        
    def onSiteInited(self):
        db=self.application.db
        #db.table('sys.locked_record').clearExistingLocks()
        db.closeConnection()
       
class Table(GnrDboTable):
    pass
        
        
class WebPage(object):
    
    def pkg_defined_method(self):
        print 'Hey'
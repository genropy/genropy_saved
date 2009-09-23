#!/usr/bin/env python
# encoding: utf-8
from gnr.app.gnrdbo import GnrDboTable, GnrDboPackage, Table_counter, Table_userobject

class Package(GnrDboPackage):
    def config_attributes(self):
        return dict(sqlschema='sys',
                    comment='sys',
                    name_short='sys',
                    name_long='sys',
                    name_full='sys')
                    
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
        db.table('sys.locked_record').clearExistingLocks()
        db.commit()
       
class Table(GnrDboTable):
    pass
        
        
class WebPage(object):
    
    def pkg_defined_method(self):
        print 'Hey'
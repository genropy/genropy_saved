#!/usr/bin/env python
# encoding: utf-8

from gnr.app.gnrdbo import GnrDboTable,GnrDboPackage,Table_userobject

class Package(GnrDboPackage):
    def config_attributes(self):
        return dict(comment='devlang package',
                    sqlschema='devlang',
                    name_short='Devlang', 
                    name_long='Developers languages', 
                    name_full='Demo: Developers languages')

    def config_db(self, pkg):
        pass

    def loginUrl(self):
        return 'devlang/login'

    def newUserUrl(self):
        return 'adm/new_user.py'

    def modifyUserUrl(self):
        return 'adm/modify_user.py'

class Table(GnrDboTable):
    pass


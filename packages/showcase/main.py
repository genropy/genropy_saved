#!/usr/bin/env python
# encoding: utf-8
from gnr.app.gnrdbo import GnrDboTable, GnrDboPackage, Table_counter, Table_userobject

class Package(GnrDboPackage):
    def config_attributes(self):
        return dict(sqlschema='showcase',
                    comment='Showcase',
                    name_short='showcase',
                    name_long='showcase',
                    name_full='showcase')

    def config_db(self, pkg):
        #you can describe here your database or separate table into classes
        pass

    def newUserUrl(self):
        return 'adm/new_user'

    def modifyUserUrl(self):
        return 'adm/modify_user'

    def loginUrl(self):
        return 'adm/login'

class Table(GnrDboTable):
    pass

class WebPage(object):
    def pkg_defined_method(self):
        print 'Hey'
#!/usr/bin/env python
# encoding: utf-8

from gnr.app.gnrdbo import GnrDboTable, GnrDboPackage, Table_counter, Table_userobject

class Package(GnrDboPackage):
    def config_attributes(self):
        return dict(sqlschema='gnrtutor',
                    comment='gnrTutor gnrtutor package',
                    name_short='gnrtutor',
                    name_long='gnrTutor',
                    full_name='gnrTutor Package')

    def config_db(self, pkg):
        pass

    def custom_type_money(self):
        return dict(dtype='N', size='12,2', default=0)

    def custom_type_percent(self):
        return dict(dtype='N', size='7,2', default=0)

    def newUserUrl(self):
        return 'adm/new_user.py'

    def modifyUserUrl(self):
        return 'adm/modify_user.py'

    def loginUrl(self):
        return 'gnrtutor/login.py'


class Table(GnrDboTable):
    def use_dbstores(self):
        return True

class Table(GnrDboTable):
    def use_dbstores(self):
        return True

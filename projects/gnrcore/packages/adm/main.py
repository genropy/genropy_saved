#!/usr/bin/env python
# encoding: utf-8

from gnr.app.gnrdbo import GnrDboTable, GnrDboPackage, Table_counter, Table_userobject
from gnr.core.gnrdict import dictExtract
import hashlib
from datetime import datetime

class Package(GnrDboPackage):
    def config_attributes(self):
        return dict(sqlschema='adm',
                    comment='Admin',
                    name_short='Adm',
                    name_long='!!Administration',
                    name_full='!!Administration Tool')

    def config_db(self, pkg):
        pass

    def authenticate(self, username, **kwargs):
        result = self.application.db.query('adm.user', columns='*',
                                           where='$username = :user AND $status != :waiting',
                                           user=username, waiting='wait', limit=1).fetch()
        if result:
            user_record = dict(result[0])
            kwargs['tags'] = user_record.pop('auth_tags')
            kwargs['pwd'] = user_record.pop('md5pwd')
            kwargs['user_id'] = user_record['id']
            kwargs['user_name'] = '%s %s' % (user_record['firstname'], user_record['lastname'])
            kwargs.update(dictExtract(user_record, 'avatar_'))
            return kwargs

    def onAuthentication(self, avatar):
        pass
        #update_md5 = self.attributes.get('update_md5',False) not in ('N','n','F','f','False','false','FALSE','No','NO','no',False)
        #if update_md5 and hasattr(avatar,'md5len') and avatar.md5len==32:
        #    self.update_md5(avatar)
        #avatar.login_pwd = None

    def onAuthenticated(self, avatar):
        pass
        #self.db.table('adm.connection').connectionLog('open')

        #def update_md5(self,avatar):
        #    md5_userid=hashlib.md5(str(avatar.userid)).hexdigest()
        #    new_pass=hashlib.md5(avatar.login_pwd+md5_userid).hexdigest()+':'+md5_userid
        #    self.application.db.table('adm.user').update(dict(id=avatar.userid,md5pwd=new_pass))
        #    self.application.db.commit()

    def newUserUrl(self):
        return 'adm/new_user'

    def modifyUserUrl(self):
        return 'adm/modify_user'

    def loginUrl(self):
        return 'adm/login'

    def onApplicationInited(self):
        pass

    def onSiteInited(self):
        db = self.application.db
        db.table('adm.connection').closePendingConnections(end_ts=datetime.now(), end_reason='sys_restart')
        db.table('adm.served_page').closePendingPages(end_ts=datetime.now(), end_reason='sys_restart')
        db.closeConnection()

class Table(GnrDboTable):
    pass

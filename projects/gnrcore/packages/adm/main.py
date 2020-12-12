#!/usr/bin/env python
# encoding: utf-8

from gnr.app.gnrdbo import GnrDboTable, GnrDboPackage
from gnr.core.gnrdict import dictExtract

class Package(GnrDboPackage):
    def config_attributes(self):
        return dict(sqlschema='adm',
                    comment='Admin',
                    name_short='Adm',
                    name_long='!!Administration',
                    name_full='!!Administration Tool')

    def config_db(self, pkg):
        pass

    def required_packages(self):
        return ['gnrcore:sys']

    def authenticate(self, username,**kwargs):
        tblobj = self.db.table('adm.user')
        def cb(cache=None,identifier=None,**kwargs):
            if identifier in cache:
                return cache[identifier],True
            result = tblobj.query(columns="""*,$all_tags,@group_code.custom_menu AS menubag,
                                                @group_code.rootpage AS group_rootpage""",
                                        where='$username = :user',user=username, limit=1).fetch()
            kwargs = dict()
            if result:
                user_record = dict(result[0])
                kwargs['tags'] = user_record.pop('all_tags')
                kwargs['pwd'] = user_record.pop('md5pwd')
                kwargs['status'] = user_record['status']
                kwargs['email'] = user_record['email']
                kwargs['firstname'] = user_record['firstname']
                kwargs['lastname'] = user_record['lastname']
                kwargs['user_id'] = user_record['id']
                kwargs['group_code'] = user_record['group_code']
                kwargs['avatar_rootpage'] = user_record['avatar_rootpage']  or user_record['group_rootpage']
                kwargs['locale'] = user_record['locale'] or self.application.config('default?client_locale')
                kwargs['user_name'] = '%s %s' % (user_record['firstname'], user_record['lastname'])
                kwargs['user_record'] = user_record
                kwargs['menubag'] = user_record['menubag']
                kwargs.update(dictExtract(user_record, 'avatar_'))
                allowed_ip = self.db.table('adm.user_access_group').allowedUser(user_record['id'])
                if allowed_ip is not None:
                    kwargs['allowed_ip'] = allowed_ip
                cache[identifier] = kwargs
            return kwargs,False
        authkwargs = tblobj.tableCachedData('user_authenticate',cb,identifier=username)
        return authkwargs


        
    def onAuthentication(self, avatar):
        pass

    def onAuthenticated(self, avatar):
        pass

    def onExternalUser(self,externalUser=None):
        self.db.table('adm.user').syncExternalUser(externalUser)
        
    def newUserUrl(self):
        return 'adm/new_user'

    def modifyUserUrl(self):
        return 'adm/modify_user'

    def loginUrl(self):
        return 'adm/login'

    
class Table(GnrDboTable):
    def use_dbstores(self,forced_dbstore=None, env_forced_dbstore=None,**kwargs):
        return forced_dbstore or env_forced_dbstore or False

    def isInStartupData(self):
        return False
        

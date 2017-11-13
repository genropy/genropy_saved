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
    
    def authenticate(self, username,**kwargs):
        tblobj = self.db.table('adm.user')
        def cb(cache=None,identifier=None,**kwargs):
            if identifier in cache:
                return cache[identifier],True
            result = tblobj.query(columns='*,$all_tags',where='$username = :user',user=username, limit=1).fetch()
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
                kwargs['avatar_rootpage'] = user_record['avatar_rootpage']
                kwargs['locale'] = user_record['locale'] or self.application.config('default?client_locale')
                kwargs['user_name'] = '%s %s' % (user_record['firstname'], user_record['lastname'])
                kwargs.update(dictExtract(user_record, 'avatar_'))
                access_groups = self.db.table('adm.user_access_group').query(where='$user_id=:uid',uid=user_record['id'],
                                                            columns='@access_group_code.allowed_ip AS allowed_ip').fetch()
                allowed_ip = set([])
                for ag in access_groups:
                    allowed_ip = allowed_ip.union(set(ag['allowed_ip'].split(',') if ag['allowed_ip'] else []))
                if allowed_ip:
                    kwargs['allowed_ip'] = ','.join(allowed_ip)
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

    def onSiteInited(self):
        touchRecords = self.db.table('adm.htag').touchRecords(where='$hierarchical_code IS NULL')
        if touchRecords:
            self.db.commit()


class Table(GnrDboTable):
    def use_dbstores(self,forced_dbstore=None, env_forced_dbstore=None,**kwargs):
        return forced_dbstore or env_forced_dbstore or False

    def isInStartupData(self):
        return False
        

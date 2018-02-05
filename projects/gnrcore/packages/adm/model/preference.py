# encoding: utf-8
from __future__ import with_statement
from gnr.core.gnrbag import Bag
from gnr.sql.gnrsql_exceptions import RecordNotExistingError

MAIN_PREFERENCE = '_mainpref_'

class Table(object):
    def config_db(self, pkg):
        tbl = pkg.table('preference', pkey='code', name_long='!!Preference',
                        name_plural='!!Preference')
        self.sysFields(tbl, id=False)
        tbl.column('code', size='12', name_long='!!Code')
        tbl.column('data', 'X', name_long='!!Data')

        # NOTE: these are private APIs, please use <your_package>.getPreference()

        # and <your_package>.setPreference() to get and set preferences.


    def getMainStorePreference(self):
        result = self.db.application.cache.get(MAIN_PREFERENCE)
        if result is None:
            result = self.loadPreference()['data']
            self.db.application.cache[MAIN_PREFERENCE] = result
        return result.deepcopy()
    
    def getStorePreferences(self):
        storename = self.db.currentEnv.get('storename')
        pref_cache_key = '_storepref_%s' %storename
        preference = self.db.application.cache.get(pref_cache_key)
        if preference is None:
            preference = self.getMainStorePreference()
            store_preference =  self.db.package('multidb').getStorePreference()
            preference.update(store_preference)
            self.db.application.cache[pref_cache_key] = preference
        return preference.deepcopy()

    def getPreference(self, path, pkg=None, dflt=None):
        prefdata = self.getStorePreferences() if not self.db.usingRootstore() else self.getMainStorePreference()
        if path=='*':
            path = None
            pkg = None
        if pkg:
            prefdata = prefdata[pkg] or Bag()
        if not path:
            return prefdata
        if path:
            prefdata = prefdata[path]
        return  dflt if prefdata is None else prefdata    
  
    def envPreferences(self,username=None):
        preferences = self.getPreference('*') or dict()
        if username:
            userpref = self.db.table('adm.user').getPreference(path='*',username=username)
            if userpref:
                if preferences:
                    preferences.update(userpref)
                else:
                    preferences = userpref
        for pkgId,pkgpref in preferences.items():
            pkgObj = self.db.application.packages[pkgId]
            if not pkgObj:continue
            for k,v in pkgObj.envPreferences().items():
                if pkgpref.getNode(k):
                    pkgpref.setAttr(k,dbenv=v)
        return preferences.filter(lambda n: n.attr.get('dbenv')) if preferences else None

    def setPreference(self, path, value, pkg='',_attributes=None,**kwargs):
        with self.db.tempEnv(connectionName='system',storename=self.db.rootstore):
            with self.recordToUpdate(MAIN_PREFERENCE) as record:
                record.setItem('data.%s.%s' % (pkg, path), value,_attributes=_attributes,**kwargs)
            self.db.commit()

    def loadPreference(self, pkey=MAIN_PREFERENCE, for_update=False):
        with self.db.tempEnv(connectionName='system',storename=self.db.rootstore):
            try:
                record = self.record(pkey=pkey, for_update=for_update).output('bag')
            except RecordNotExistingError:
                record = self.newrecord(code=pkey, data=Bag())
        return record

    def trigger_onUpdated(self,record=None,old_record=None):
        if self.fieldsChanged('data',record,old_record):
            self.db.application.pkgBroadcast('onSavedPreferences',preferences=record['data'])
            site = getattr(self.db.application,'site',None)
            if site:
                site.process_cmd.clearApplicationCache(MAIN_PREFERENCE)
                if site.currentPage:
                    site.currentPage.setInClientData('gnr.serverEvent.refreshNode', value='gnr.app_preference', filters='*',
                             fired=True, public=True)
# encoding: utf-8
from __future__ import with_statement
from gnr.core.gnrbag import Bag
from gnr.core.gnrlang import MandatoryException
from gnr.sql.gnrsql_exceptions import RecordNotExistingError
from datetime import datetime

MAIN_PREFERENCE = '_mainpref_'

class Table(object):
    def config_db(self, pkg):
        tbl = pkg.table('preference', pkey='code', name_long='!!Preference',
                        name_plural='!!Preference')
        self.sysFields(tbl, id=False)
        tbl.column('code', size='12', name_long='!!Code')
        tbl.column('data', 'X', name_long='!!Data',_sendback=True)

        # NOTE: these are private APIs, please use <your_package>.getPreference()

        # and <your_package>.setPreference() to get and set preferences.


    def getMainStorePreference(self):
        result = self.db.application.cache.getItem(MAIN_PREFERENCE)
        if not result:
            result = self.loadPreference()['data']
            self.db.application.cache.setItem(MAIN_PREFERENCE, result)
        return result.deepcopy()
    
    def getStorePreferences(self):
        storename = self.db.currentEnv.get('storename')
        pref_cache_key = '_storepref_%s' %storename
        preference = None
        if not self.db.application.cache.expiredItem(MAIN_PREFERENCE):
            preference = self.db.application.cache.getItem(pref_cache_key)
        if not preference:
            preference = self.getMainStorePreference()
            store_preference =  self.db.package('multidb').getStorePreference()
            for pkgid,pkgobj in self.db.application.packages.items():
                multidb_pref = pkgobj.attributes.get('multidb_pref')
                if multidb_pref:
                    pkgstorepref = store_preference[pkgid] or Bag()
                    if multidb_pref is True:
                        preference[pkgid] = pkgstorepref
                    else:
                        preference[pkgid] = preference[pkgid] or Bag()
                        preference[pkgid].update(pkgstorepref,ignoreNone=True)
                
            self.db.application.cache.setItem(pref_cache_key,preference)
        return preference.deepcopy()

    def getPreference(self, path, pkg=None, dflt=None, mandatoryMsg=None):
        prefdata = self.getStorePreferences() if self.db.package('multidb') \
                    and not self.db.usingRootstore() else self.getMainStorePreference()
        if path=='*':
            path = None
            pkg = None
        if pkg:
            prefdata = prefdata[pkg] or Bag()
        if not path:
            return prefdata
        if path:
            prefdata = prefdata[path]
            if mandatoryMsg and prefdata is None:
                raise MandatoryException(description=mandatoryMsg)
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

    def initPkgPref(self,pkg=None,pkgpref=None):
        if self.db.usingRootstore() or not self.db.application.packages[pkg].attributes.get('multidb_pref'):
            self.setPreference(pkg=pkg,value=pkgpref) 
        else:
            self.db.package('multidb').setStorePreference(pkg=pkg,value=pkgpref)

    def setPreference(self, path=None, value=None, pkg='',_attributes=None,**kwargs):
        with self.db.tempEnv(connectionName='system',storename=self.db.rootstore):
            with self.recordToUpdate(MAIN_PREFERENCE) as record:
                l = ['data',pkg]
                if path:
                    l.append(path)
                record.setItem('.'.join(l), value,_attributes=_attributes,**kwargs)
            self.db.commit()

    def loadPreference(self, pkey=MAIN_PREFERENCE, for_update=False):
        with self.db.tempEnv(connectionName='system',storename=self.db.rootstore):
            try:
                record = self.record(pkey=pkey, for_update=for_update).output('bag')
            except RecordNotExistingError:
                record = self.newrecord(code=pkey, data=Bag())
                self.insert(record)
                self.db.commit()
        return record

    def trigger_onUpdated(self,record=None,old_record=None):
        if self.fieldsChanged('data',record,old_record):
            self.db.application.pkgBroadcast('onSavedPreferences',preferences=record['data'])
            self.db.application.cache.updatedItem(MAIN_PREFERENCE)
            site = getattr(self.db.application,'site',None)
            if site and site.currentPage:
                site.currentPage.setInClientData('gnr.serverEvent.refreshNode', value='gnr.app_preference', filters='*',
                             fired=True, public=True)

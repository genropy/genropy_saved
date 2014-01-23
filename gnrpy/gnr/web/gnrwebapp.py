import os

from gnr.core.gnrbag import Bag
from gnr.app.gnrapp import GnrApp
#from gnr.core.gnrlang import gnrImport

class GnrWsgiWebApp(GnrApp):
    def __init__(self, *args, **kwargs):
        if 'site' in kwargs:
            self.site = kwargs.get('site')
            kwargs.pop('site')
        else:
            self.site = None
        self._siteMenuDict = dict()
        super(GnrWsgiWebApp, self).__init__(*args, **kwargs)

    def notifyDbEvent(self, tblobj, record, event, old_record=None):
        super(GnrWsgiWebApp, self).notifyDbEvent(tblobj, record, event, old_record=old_record)

    def onDbCommitted(self):
        super(GnrWsgiWebApp, self).onDbCommitted()
        dbeventsDict= self.db.currentEnv.pop('dbevents',None)
        if dbeventsDict:
            page = self.site.currentPage
            tables = [k for k,v in dbeventsDict.items() if v]
            subscribed_tables = self.site.register.filter_subscribed_tables(tables,register_name='page')
            if subscribed_tables:
                for table in set(tables).difference(subscribed_tables):
                    dbeventsDict.pop(table)         
                for table,dbevents in dbeventsDict.items():
                    dbeventsDict[table] = self._compress_dbevents(dbevents)
                self.site.register.notifyDbEvents(dbeventsDict,register_name='page',origin_page_id=page.page_id if page else None)
            self.db.updateEnv(env_transaction_id= None,dbevents=None)

    def _compress_dbevents(self,dbevents):
        event_index = dict()
        result = list()
        filter_ignored = False
        for event in dbevents:
            pkey = event['pkey']
            eventype = event['dbevent']
            if not pkey in event_index:
                event_index[pkey] = len(result)
                result.append(event)
            else:
                event_to_update = result[event_index[pkey]]
                if eventype=='U':
                    event.pop('dbevent')
                elif eventype=='D' and event_to_update['dbevent'] == 'I':
                    event['dbevent'] = 'X'
                    filter_ignored = True
                event_to_update.update(event)
        return filter(lambda r: r['dbevent']!='X', result) if filter_ignored else result

    def _get_pagePackageId(self, filename):
        _packageId = None
        fpath, last = os.path.split(os.path.realpath(filename))
        while last and last != 'webpages':
            fpath, last = os.path.split(fpath)
        if last == 'webpages':
            _packageId = self.packagesIdByPath[fpath]
        if not _packageId:
            _packageId = self.config.getAttr('packages', 'default')
        return _packageId

    def newUserUrl(self):
        if self.config['authentication?canRegister']:
            authpkg = self.authPackage()
            if authpkg and hasattr(authpkg, 'newUserUrl'):
                return authpkg.newUserUrl()

    def modifyUserUrl(self):
        authpkg = self.authPackage()
        if authpkg and hasattr(authpkg, 'modifyUserUrl'):
            return authpkg.modifyUserUrl()

    def loginUrl(self):
        authpkg = self.authPackage()
        loginUrl = ''
        if authpkg and hasattr(authpkg, 'loginUrl'):
            loginUrl = authpkg.loginUrl()
        return loginUrl

    def debugger(self, debugtype, **kwargs):
        self.site.debugger(debugtype, **kwargs)

    def _get_siteMenu(self):
        dbstore = self.site.currentPage.dbstore
        siteMenu = self._siteMenuDict.get(dbstore)
        if not siteMenu:
            siteMenu = self._buildSiteMenu()
            self._siteMenuDict[dbstore] = siteMenu
        return siteMenu

    siteMenu = property(_get_siteMenu)

    def _buildSiteMenu(self):
        menubag = self.config['menu']
        if not menubag:
            menubag = Bag()
            for pathlist, node in self.site.automap.getIndex():
                attr = dict(label=node.getAttr('name') or node.label.capitalize())
                if isinstance(node.getValue(), Bag):
                    attr['basepath'] = '/%s' % ('/'.join(pathlist))
                else:
                    attr['file'] = node.label
                menubag.setItem(pathlist, None, attr)
        menubag = self._buildSiteMenu_prepare(menubag)
        return menubag

    def _buildSiteMenu_prepare(self, menubag, basepath=None):
        basepath = basepath or []
        result = Bag()
        for node in menubag.nodes:
            value = node.getStaticValue()
            attributes = {}
            attributes.update(node.getAttr())
            currbasepath = basepath
            if 'basepath' in attributes:
                newbasepath = attributes.pop('basepath')
                if newbasepath.startswith('/'):
                    currbasepath = [self.site.home_uri + newbasepath[1:]]
                else:
                    currbasepath = basepath + [newbasepath]
            if isinstance(value, Bag):
                value = self._buildSiteMenu_prepare(value, currbasepath)
            else:
                value = None
                filepath = attributes.get('file')
                if filepath:
                    if not filepath.startswith('/'):
                        attributes['file'] = os.path.join(*(currbasepath + [filepath]))
                    else:
                        attributes['file'] = self.site.home_uri + filepath.lstrip('/')
            result.setItem(node.label, value, attributes)
        return result

    def setPreference(self, path, data, pkg):
        if self.db.package('adm'):
            self.db.table('adm.preference').setPreference(path, data, pkg=pkg)

    def getPreference(self, path, pkg, dflt=''):
        if self.db.package('adm'):
            return self.db.table('adm.preference').getPreference(path, pkg=pkg, dflt=dflt)
    
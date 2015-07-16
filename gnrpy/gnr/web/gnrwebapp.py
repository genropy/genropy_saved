import os

from gnr.core.gnrbag import Bag,DirectoryResolver
from gnr.app.gnrapp import GnrApp
#from gnr.core.gnrlang import gnrImport
from gnr.core.gnrlang import getUuid

class GnrWsgiWebApp(GnrApp):
    def __init__(self, *args, **kwargs):
        if 'site' in kwargs:
            self.site = kwargs.get('site')
            kwargs.pop('site')
        else:
            self.site = None
        self._siteMenuDict = dict()
        super(GnrWsgiWebApp, self).__init__(*args, **kwargs)

    def notifyDbUpdate(self,tblobj,recordOrPkey=None,**kwargs):
        if isinstance(recordOrPkey,list):
            records = recordOrPkey
        elif not recordOrPkey and kwargs:
            records = tblobj.query(**kwargs).fetch()
        else:
            broadcast = tblobj.attributes.get('broadcast')
            if broadcast is False:
                return
            if isinstance(recordOrPkey,basestring):
                if isinstance(broadcast,basestring):
                    records = [tblobj.record(pkey=recordOrPkey).output('dict')]
                else:
                    records = [{tblobj.pkey:recordOrPkey}]
            else:
                records = [recordOrPkey]
        for record in records:
            self.application.notifyDbEvent(tblobj, record, 'U')

    def notifyDbEvent(self, tblobj, record, event, old_record=None):
        """TODO
        
        :param tblobj: the :ref:`database table <table>` object
        :param record: TODO
        :param event: TODO
        :param old_record: TODO. """
        currentEnv = self.db.currentEnv
        if currentEnv.get('hidden_transaction'):
            return
        if not currentEnv.get('env_transaction_id'):
            self.db.updateEnv(env_transaction_id= getUuid(),dbevents=dict())
        broadcast = tblobj.attributes.get('broadcast')
        if broadcast is not False and broadcast != '*old*':
            dbevents=currentEnv['dbevents']
            r=dict(dbevent=event,pkey=record.get(tblobj.pkey),old_pkey=old_record.get(tblobj.pkey) if old_record else None)
            if broadcast and broadcast is not True:
                for field in broadcast.split(','):
                    newvalue = record.get(field)
                    r[field] = self.catalog.asTypedText(newvalue) #2011/01/01::D
                    if old_record:
                        oldvalue = old_record.get(field)
                        if newvalue!=oldvalue:
                            r['old_%s' %field] = self.catalog.asTypedText(old_record.get(field))
            dbevents.setdefault(tblobj.fullname,[]).append(r)
        audit_mode = tblobj.attributes.get('audit')
        if audit_mode:
            self.db.table('adm.audit').audit(tblobj,event,audit_mode=audit_mode,record=record, old_record=old_record)
                
   
    def onDbCommitted(self):
        super(GnrWsgiWebApp, self).onDbCommitted()
        dbeventsDict= self.db.currentEnv.pop('dbevents',None)
        if dbeventsDict:
            page = self.site.currentPage
            tables = [k for k,v in dbeventsDict.items() if v]
            subscribed_tables = self.site.getSubscribedTables(tables)
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


    def checkAllowedIp(self,allowed_ip):
        "override"
        currentPage = self.site.currentPage
        iplist = currentPage.connection.ip.split('.')
        for ip in allowed_ip.split(','):
            ipcheck = ip.split('.') 
            if iplist[0:len(ipcheck)] == ipcheck:
                return True
        return False

    def loginUrl(self):
        authpkg = self.authPackage()
        loginUrl = ''
        if authpkg and hasattr(authpkg, 'loginUrl'):
            loginUrl = authpkg.loginUrl()
        return loginUrl

    def sqlDebugger(self, **kwargs):
        self.site.sqlDebugger(**kwargs)

    def clearSiteMenu(self):
        self._siteMenuDict = dict()

    def _get_siteMenu(self):
        dbstore = self.site.currentPage.dbstore
        siteMenu = self._siteMenuDict.get(dbstore)
        if not siteMenu:
            siteMenu = self.compileSiteMenu(self.config['menu'] or self.applicationMenuBag())
            self._siteMenuDict[dbstore] = siteMenu
        return siteMenu

    siteMenu = property(_get_siteMenu)


    def compileSiteMenu(self, menubag, basepath=None,level=None):
        basepath = basepath or []
        level = level or 0
        result = Bag()
        for node in menubag.nodes:
            attributes = {}
            attributes.update(node.getAttr())
            currbasepath = basepath
            if 'pkg' in attributes:
                if 'dir' in attributes:
                    url_info = self.site.getUrlInfo([attributes['pkg'], attributes['dir']])
                    dirpath=os.path.join(url_info.basepath,*url_info.request_args)  
                    value=DirectoryResolver(dirpath,cacheTime=10,
                                                include='*.py', exclude='__*,.*',dropext=True,readOnly=False)
                    currbasepath = [attributes['pkg'],attributes['dir']]
                else:
                    value = self.packages[attributes['pkg']].pkgMenu['#0']
            else:
                value = node.getStaticValue()
            if 'basepath' in attributes:
                newbasepath = attributes.pop('basepath')
                if newbasepath.startswith('/'):
                    currbasepath = [self.site.home_uri + newbasepath[1:]]
                else:
                    currbasepath = basepath + [newbasepath]
            if isinstance(value, Bag):
                value = self.compileSiteMenu(value, currbasepath,level=level+1)
            elif not isinstance(value, DirectoryResolver):
                value = None
                filepath = attributes.get('file')
                if filepath:
                    if not filepath.startswith('/'):
                        attributes['file'] = os.path.join(*(currbasepath + [filepath]))
                    else:
                        attributes['file'] = self.site.home_uri + filepath.lstrip('/')
            result.setItem(node.label, value, attributes)
        if len(result) == 1 and not level:
            result = result['#0']
        return result


    @property
    def locale(self):
        return self.site.locale

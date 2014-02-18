#-*- coding: UTF-8 -*-  
#--------------------------------------------------------------------------
# package           : GenroPy web - see LICENSE for details
# module gnrwebcore : core module for genropy web framework
# Copyright (c)     : 2004 - 2007 Softwell sas - Milano 
# Written by    : Giovanni Porcari, Michele Bertoldi
#                 Saverio Porcari, Francesco Porcari , Francesco Cavazzana
#--------------------------------------------------------------------------
#This library is free software; you can redistribute it and/or
#modify it under the terms of the GNU Lesser General Public
#License as published by the Free Software Foundation; either
#version 2.1 of the License, or (at your option) any later version.

#This library is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
#Lesser General Public License for more details.

#You should have received a copy of the GNU Lesser General Public
#License along with this library; if not, write to the Free Software
#Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA

import Pyro4
from datetime import datetime
import time
from gnr.core.gnrbag import Bag,BagResolver
from gnr.web.gnrwebpage import ClientDataChange
from gnr.core.gnrclasses import GnrClassCatalog

try:
    import cPickle as pickle
except ImportError:
    import pickle
import os

import re

BAG_INSTANCE = Bag()

PYRO_HOST = 'localhost'
PYRO_PORT = 40004
PYRO_HMAC_KEY = 'supersecretkey'
PYRO_MULTIPLEX = True
LOCK_MAX_RETRY = 100
RETRY_DELAY = 0.01

def remotebag_wrapper(func):
    def decore(self,*args,**kwargs):
        if self.rootpath:
            kwargs['_pyrosubbag'] = self.rootpath
        kwargs['_siteregister_register_name'] = self.register_name
        kwargs['_siteregister_register_item_id'] = self.register_item_id
        return func(self,*args,**kwargs)
    return decore

class BaseRemoteObject(object):
    def onSizeExceeded(self, msg_size, method, vargs, kwargs):
        print '[%i-%i-%i %i:%i:%i]-----%s-----'%((time.localtime()[:6])+(self.__class__.__name__.upper(),))
        print 'Message size:', msg_size
        print 'Method :', method
        print 'vargs, kwargs', vargs, kwargs
        print '**********'

#------------------------------- REMOTEBAG server SIDE ---------------------------
class RemoteStoreBagHandler(BaseRemoteObject):
    def __init__(self,siteregister):
        self.siteregister = siteregister


    def __getattr__(self,name):
        if name=='_pyroId':
            return self._pyroId
        def decore(*args,**kwargs):
            register_name = kwargs.pop('_siteregister_register_name',None)
            register_item_id = kwargs.pop('_siteregister_register_item_id',None)
            store = self.siteregister.get_item_data(register_item_id,register_name=register_name)
            if '_pyrosubbag' in kwargs:
                _pyrosubbag = kwargs.pop('_pyrosubbag')
                store = store.getItem(_pyrosubbag)
            h = getattr(store,name, None)
            if not h:
                raise AttributeError("PyroSubBag at %s has no attribute '%s'" % (_pyrosubbag,name))
            else:
                return h(*args,**kwargs)

        return decore


#------------------------------- REMOTEBAG CLIENT SIDE ---------------------------

class RemoteStoreBag(object):
    def __init__(self,uri=None,register_name=None,register_item_id=None,rootpath=None):
        self.register_name = register_name
        self.register_item_id = register_item_id
        self.rootpath = rootpath
        self.uri = uri
        self.proxy=Pyro4.Proxy(uri)

    def chunk(self,path):
        return RemoteStoreBag(uri=self.uri,register_name=self.register_name,register_item_id=self.register_item_id,rootpath=self.rootpath)
        
    @remotebag_wrapper
    def __str__(self,*args,**kwargs):
        return self.proxy.asString(*args,**kwargs)
    @remotebag_wrapper 
    def __getitem__(self,*args,**kwargs):
        return self.proxy.__getitem__(*args,**kwargs)
    @remotebag_wrapper 
    def __setitem__(self,*args,**kwargs):
        return self.proxy.__setitem__(*args,**kwargs)
    @remotebag_wrapper 
    def __len__(self,*args,**kwargs):
        return self.proxy.__len__(*args,**kwargs)
    @remotebag_wrapper 
    def __contains__(self,*args,**kwargs):
        return self.proxy.__contains__(*args,**kwargs)
    @remotebag_wrapper 
    def __eq__(self,*args,**kwargs):
        return self.proxy.__eq__(*args,**kwargs)

    def __getattr__(self,name):
        h = getattr(self.proxy,name) 
        if not callable(h):
            return h
        def decore(*args,**kwargs):
            kwargs['_pyrosubbag'] = self.rootpath
            kwargs['_siteregister_register_name'] = self.register_name
            kwargs['_siteregister_register_item_id'] = self.register_item_id
            return h(*args,**kwargs)
        return decore

#------------------------------- END REMOTEBAG  ---------------------------




class BaseRegister(BaseRemoteObject):
    """docstring for BaseRegister"""
    def __init__(self, siteregister):
        self.siteregister = siteregister
        self.registerItems = dict() 
        self.itemsData = dict()
        self.itemsTS = dict()
        self.locked_items = dict()

    def lock_item(self,register_item_id):
        #print 'locking ',self.registerName,register_item_id,
        if not register_item_id in self.locked_items:
            self.locked_items[register_item_id] = True
            #print 'ok'
            return True
        #print 'failed'
        return False

    def unlock_item(self,register_item_id):
        self.locked_items.pop(register_item_id,None)

    def addRegisterItem(self,register_item,data=None):
        register_item_id = register_item['register_item_id']
        self.registerItems[register_item_id] = register_item
        register_item['datachanges'] = list()
        register_item['datachanges_idx'] = 0
        register_item['subscribed_paths'] = set()
        data = Bag(data)
        data.subscribe('datachanges', any=lambda **kwargs:  self._on_data_trigger(register_item=register_item,**kwargs))
        self.itemsData[register_item_id] = data

    def _on_data_trigger(self, node=None, ind=None, evt=None, pathlist=None,register_item=None, **kwargs):
        if evt == 'ins':
            pathlist.append(node.label)
        path = '.'.join(pathlist)
        for subscribed in register_item['subscribed_paths']:
            if path.startswith(subscribed):
                register_item['datachanges'].append(
                        ClientDataChange(path=path, value=node.value, reason='serverChange', attributes=node.attr))
                break
    def getRemoteData(self,register_item_id):
        pass

    def updateTS(self,register_item_id):
        self.itemsTS[register_item_id] = datetime.now()

    def get_item_data(self,register_item_id):
        return self.itemsData.get(register_item_id)

    def get_item(self,register_item_id,include_data=False):
        item = self.registerItems.get(register_item_id)
        self.updateTS(register_item_id)
        if item and include_data:
            item['data'] = self.get_item_data(register_item_id)
        return item

    def exists(self,register_item_id):
        return register_item_id in self.registerItems

    def keys(self):
        return self.registerItems.keys()

    def items(self,include_data=None):
        if not include_data:
            return self.registerItems.items()
        return [(k,self.get_item(k,include_data=True)) for k in self.keys()]

    def values(self,include_data=False):
        if not include_data:
            return self.registerItems.values()
        return [self.get_item(k,include_data=True) for k in self.keys()]

    def refresh(self,register_item_id,last_user_ts=None,last_rpc_ts=None,refresh_ts=None):
        item = self.registerItems.get(register_item_id)
        if not item:
            #print 'missing register item ',register_item_id,self.registerName
            return 
        
        item['last_user_ts'] = max(item['last_user_ts'],last_user_ts) if item.get('last_user_ts') else last_user_ts
        item['last_rpc_ts'] = max(item['last_rpc_ts'],last_rpc_ts) if item.get('last_rpc_ts') else last_rpc_ts
        item['last_refresh_ts'] = max(item['last_refresh_ts'],refresh_ts) if item.get('last_refresh_ts') else refresh_ts
        return item

    @property
    def registerName(self):
        return self.__class__.__name__


    def drop_item(self,register_item_id):
        register_item = self.registerItems.pop(register_item_id,None)
        self.itemsData.pop(register_item_id,None)
        self.itemsTS.pop(register_item_id,None)
        return register_item

    def update_item(self,register_item_id,upddict=None):
        register_item = self.get_item(register_item_id)
        register_item.update(upddict)
        return register_item

    def get_datachanges(self,register_item_id,reset=False):
        register_item = self.get_item(register_item_id)
        if not register_item:
            return
        datachanges = register_item['datachanges']
        if reset:
            register_item['datachanges'] = []
            register_item['datachanges_idx'] = 0
        return datachanges

    def reset_datachanges(self,register_item_id):
        return self.update_item(register_item_id,dict(datachanges=list(),datachanges_idx=0))


    def set_datachange(self,register_item_id, path, value=None, attributes=None, fired=False, reason=None, replace=False, delete=False):
        register_item = self.get_item(register_item_id)
        datachanges = register_item['datachanges']
        register_item['datachanges_idx'] = register_item.get('datachanges_idx', 0)
        register_item['datachanges_idx'] += 1
        datachange = ClientDataChange(path, value, attributes=attributes, fired=fired,
                                      reason=reason, change_idx=register_item['datachanges_idx'],
                                      delete=delete)
        if replace and datachange in datachanges:
            datachanges.pop(datachanges.index(datachange))
        datachanges.append(datachange)

    def drop_datachanges(self,register_item_id, path):
        register_item = self.get_item(register_item_id)
        datachanges = register_item['datachanges']
        datachanges[:] = [dc for dc in datachanges if not dc.path.startswith(path)]

    def subscribe_path(self, register_item_id,path):
        register_item = self.get_item(register_item_id)
        register_item['subscribed_paths'].add(path)

    def get_dbenv(self,register_item_id):
        data = self.get_item_data(register_item_id)
        dbenvbag = data.getItem('dbenv') or Bag()
        dbenvbag.update((data.getItem('rootenv') or Bag()))     
        def addToDbEnv(n,_pathlist=None):
            if n.attr.get('dbenv'):
                path = n.label if n.attr['dbenv'] is True else n.attr['dbenv']
                dbenvbag[path] = n.value
        _pathlist = []
        data.walk(addToDbEnv,_pathlist=_pathlist)
        return dbenvbag
      
    def dump(self,storagefile):

        pickle.dump(self.registerItems, storagefile)
        pickle.dump(self.itemsData, storagefile)
        pickle.dump(self.itemsTS, storagefile)
        pickle.dump(self.locked_items, storagefile)

    def load(self,storagefile):
        self.registerItems = pickle.load(storagefile)
        self.itemsData = pickle.load(storagefile)
        self.itemsTS = pickle.load(storagefile)
        self.locked_items = pickle.load(storagefile)



class UserRegister(BaseRegister):
    """docstring for UserRegister"""
    def create(self, user, user_id=None,user_name=None,user_tags=None,avatar_extra=None):
        register_item = dict(
                register_item_id=user,
                start_ts=datetime.now(),
                user=user,
                user_id=user_id,
                user_name=user_name,
                user_tags=user_tags,
                avatar_extra=avatar_extra,
                register_name='user')
        self.addRegisterItem(register_item)
        return register_item
        
    def drop(self,user):
        self.siteregister.drop_connections(user)
        self.drop_item(user)

class ConnectionRegister(BaseRegister):
    """docstring for ConnectionRegister"""
    def create(self, connection_id, connection_name=None,user=None,user_id=None,
                            user_name=None,user_tags=None,user_ip=None,user_agent=None,browser_name=None):
        register_item = dict(
                register_item_id=connection_id,
                start_ts=datetime.now(),
                connection_name = connection_name,
                user= user, 
                user_id= user_id,
                user_name = user_name,
                user_tags = user_tags,
                user_ip=user_ip,
                user_agent=user_agent,
                browser_name=browser_name,
                register_name='connection')

        self.addRegisterItem(register_item)
        return register_item

    def drop(self,register_item_id=None,cascade=None):
        self.siteregister.drop_pages(register_item_id)
        register_item = self.drop_item(register_item_id)
        if cascade:
            user = register_item['user']
            keys = self.user_connection_keys(user)
            if not keys:
                self.siteregister.drop_user(user)

    def user_connection_keys(self,user):
        return [k for k,v in self.items() if v['user'] == user]

    def user_connection_items(self,user):
        return [(k,v) for k,v in self.items() if v['user'] == user]



    def connections(self,user=None,include_data=None):
        connections = self.values(include_data=include_data)
        if user:
            connections = [v for v in connections if v['user'] == user]
        return connections
        

class PageRegister(BaseRegister):
    def __init__(self,*args,**kwargs):
        super(PageRegister, self).__init__(*args,**kwargs)
        self.pageProfilers = dict()

    def create(self, page_id,pagename=None,connection_id=None,subscribed_tables=None,user=None,user_ip=None,user_agent=None ,data=None):
        register_item_id = page_id
        start_ts = datetime.now()
        if subscribed_tables:
            subscribed_tables = subscribed_tables.split(',')
        register_item = dict(
                register_item_id=register_item_id,
                pagename=pagename,
                connection_id=connection_id,
                start_ts=start_ts,
                subscribed_tables=subscribed_tables or [],
                user=user,
                user_ip=user_ip,
                user_agent=user_agent,
                datachanges=list(),
                subscribed_paths=set(),
                register_name='page')
        self.addRegisterItem(register_item,data=data)
        return register_item


    def drop(self,register_item_id=None,cascade=None):
        register_item = self.drop_item(register_item_id)
        self.pageProfilers.pop(register_item_id,None)
        if cascade:
            connection_id = register_item['connection_id']
            n = self.connection_page_keys(connection_id)
            if not n:
                self.siteregister.drop_connection(connection_id)

    def filter_subscribed_tables(self,table_list):
        s = set()
        for k,v in self.items():
            s.update(v['subscribed_tables'])
        return list(s.intersection(table_list))

    def subscribed_table_page_keys(self,table):
        return [k for k,v in self.items() if table in v['subscribed_tables']]

    def subscribed_table_page_items(self,table):
        return [(k,v) for k,v in self.items() if table in v['subscribed_tables']]

    def subscribed_table_pages(self,table):
        return [v for k,v in self.items() if table in v['subscribed_tables']]

    def connection_page_keys(self,connection_id):
        return [k for k,v in self.items() if v['connection_id'] == connection_id]

    def connection_page_items(self,connection_id):
        return [(k,v) for k,v in self.items() if v['connection_id'] == connection_id]

    def pages(self,connection_id=None,user=None,include_data=None,filters=None):
        pages = self.values(include_data=include_data)
        if connection_id:
            pages = [v for v in pages if v['connection_id'] == connection_id]
        if user:
            pages = [v for v in pages if v['user'] == user]
        if not filters or filters == '*':
            return pages
        fltdict = dict()
        for flt in filters.split(' AND '):
            fltname, fltvalue = flt.split(':', 1)
            fltdict[fltname] = fltvalue
        filtered = []
        def checkpage(page, fltname, fltval):
            value = page[fltname]
            if not value:
                return
            if not isinstance(value, basestring):
                return fltval == value
            try:
                return re.match(fltval, value)
            except:
                return False
        for page in pages:
            page = Bag(page)
            for fltname, fltval in fltdict.items():
                if checkpage(page, fltname, fltval):
                    filtered.append(page)
        return filtered

    def updatePageProfilers(self,page_id,pageProfilers):
        self.pageProfilers[page_id] = pageProfilers 

    def setStoreSubscription(self,page_id,storename=None,client_path=None,active=None):
        register_item_data = self.get_item_data(page_id)
        subscription_path = '_subscriptions.%s' %storename
        storesub = register_item_data.getItem(subscription_path)
        if storesub is None:
            storesub = dict()
            register_item_data.setItem(subscription_path, storesub)
        pathsub = storesub.setdefault(client_path, {})
        pathsub['on'] = active

    def subscribeTable(self,page_id,table=None,subscribe=None,subscribeMode=None):
        register_item = self.get_item(page_id)
        subscribed_tables = register_item['subscribed_tables']
        if subscribe:
            if not table in subscribed_tables:
                subscribed_tables.append(table)
        else:
            if table in subscribed_tables:
                subscribed_tables.remove(table)

    def notifyDbEvents(self,dbeventsDict=None,origin_page_id=None):
        for table,dbevents in dbeventsDict.items():
            if not dbevents: continue
            table_code = table.replace('.', '_')
            subscribers = self.subscribed_table_pages(table)
            if not subscribers: continue
            for page in subscribers:
                self.set_datachange(page['register_item_id'],'gnr.dbchanges.%s' %table_code, dbevents,attributes=dict(from_page_id=origin_page_id))

    def setPendingContext(self,page_id,pendingContext):
        data = self.get_item_data(page_id)
        for serverpath,value,attr in pendingContext:
            data.setItem(serverpath, value, attr)
            self.subscribe_path(page_id,serverpath)

    def updateLocalization(self,page_id=None,localizer_dict=None):
        localization = {}
        data = self.get_item_data(page_id)
        localization.update(data.getItem('localization') or {})
        localization.update(localizer_dict)
        data.setItem('localization', localization)

    def pageInMaintenance(self,page_id=None):
        page_item = self.get_item(page_id)
        if not page_item:
            return
        user = page_item['user']
        return self.siteregister.isInMaintenance(user)

    def setInClientData(self,path, value=None, attributes=None, page_id=None, filters=None,
                        fired=False, reason=None, public=False, replace=False):
        if filters:
            pages = [p['register_item_id'] for p in self.pages(filters=filters)]
        else:
            pages = [page_id]
        for page_id in pages:
            if isinstance(path, Bag):
                changeBag = path
                for changeNode in changeBag:
                    attr = changeNode.attr
                    self.set_datachange(page_id,path=attr.pop('_client_path'),value=changeNode.value,attributes=attr, fired=attr.pop('fired', None))
            else:
                self.set_datachange(page_id,path=path,value=value,reason=reason, attributes=attributes, fired=fired)

class SiteRegister(BaseRemoteObject):
    def __init__(self,server,sitename=None,storage_path=None):
        self.server = server
        self.page_register = PageRegister(self)
        self.connection_register = ConnectionRegister(self)
        self.user_register = UserRegister(self)
        self.remotebag_handler = RemoteStoreBagHandler(self)
        self.server.daemon.register(self.remotebag_handler,'RemoteData')
        self.last_cleanup = time.time()
        self.sitename = sitename
        self.storage_path = storage_path
        self.catalog = GnrClassCatalog()
        self.maintenance = False
        self.allowed_users = None




    def setConfiguration(self,cleanup=None):
        cleanup = cleanup or dict()
        self.cleanup_interval = int(cleanup.get('interval') or 120)
        self.page_max_age = int(cleanup.get('page_max_age') or 120)
        self.connection_max_age = int(cleanup.get('connection_max_age')or 600)

    def new_connection(self,connection_id,connection_name=None,user=None,user_id=None,
                            user_name=None,user_tags=None,user_ip=None,user_agent=None,browser_name=None,avatar_extra=None):
        assert not self.connection_register.exists(connection_id), 'SITEREGISTER ERROR: connection_id %s already registered' % connection_id
        if not self.user_register.exists(user):
            self.new_user( user, user_id=user_id,user_name=user_name,user_tags=user_tags,avatar_extra=avatar_extra)
        connection_item = self.connection_register.create(connection_id, connection_name=connection_name,user=user,user_id=user_id,
                            user_name=user_name,user_tags=user_tags,user_ip=user_ip,user_agent=user_agent,browser_name=browser_name)

        return connection_item


    def drop_pages(self,connection_id):
        for page_id in self.connection_page_keys(connection_id):
            self.drop_page(page_id)

    def drop_page(self,page_id, cascade=None):
        return self.page_register.drop(page_id,cascade=cascade)   

    def drop_connections(self,user):
        for connection_id in self.user_connection_keys(user):
            self.drop_connection(connection_id)

    def drop_connection(self,connection_id,cascade=None):
        self.connection_register.drop(connection_id,cascade=cascade)

    def drop_user(self,user):
        self.user_register.drop(user)

    def user_connection_keys(self,user):
        return self.connection_register.user_connection_keys(user)

    def user_connection_items(self,user):
        return self.connection_register.user_connection_items(user)

    def user_connections(self,user):
        return self.connection_register.user_connections(user)

    def connection_page_keys(self,connection_id):
        return self.page_register.connection_page_keys(connection_id=connection_id)

    def connection_page_items(self,connection_id):
        return self.page_register.connection_page_items(connection_id=connection_id)

    def connection_pages(self,connection_id):
        return self.page_register.connection_pages(connection_id=connection_id)


    def new_page(self,page_id,pagename=None,connection_id=None,subscribed_tables=None,user=None,user_ip=None,user_agent=None ,data=None):
        page_item = self.page_register.create(page_id, pagename = pagename,connection_id=connection_id,user=user,
                                            user_ip=user_ip,user_agent=user_agent, data=data)
        return page_item


    def new_user(self,user=None, user_tags=None, user_id=None, user_name=None,
                               avatar_extra=None):
        user_item = self.user_register.create( user=user, user_tags=user_tags, user_id=user_id, user_name=user_name,
                               avatar_extra=avatar_extra)
        return user_item

    def subscribed_table_pages(self,table=None):
        return self.page_register.subscribed_table_pages(table)

    def pages(self, connection_id=None,user=None,index_name=None, filters=None,include_data=None):
        if index_name:
            print 'call subscribed_table_pages instead of pages'
            return self.subscribed_table_pages(index_name)
        return self.page_register.pages(connection_id=connection_id,user=user,filters=filters,include_data=include_data)
        

    def page(self,page_id):
        return self.page_register.get_item(page_id)

    def connection(self,connection_id):
        return self.connection_register.get_item(connection_id)

    def user(self,user):
        return self.user_register.get_item(user)


    def users(self,include_data=None):
        return self.user_register.values(include_data)

    def connections(self,user=None,include_data=None):
        return self.connection_register.connections(user=user,include_data=include_data)
 

    def change_connection_user(self, connection_id, user=None, user_tags=None, user_id=None, user_name=None,
                               avatar_extra=None):
        connection_item = self.connection(connection_id)

        olduser = connection_item['user']
        newuser_item = self.user(user)
        if not newuser_item:
            newuser_item = self.new_user( user=user, user_tags=user_tags, user_id=user_id, user_name=user_name,
                               avatar_extra=avatar_extra)
        connection_item['user'] = user
        connection_item['user_tags'] = user_tags
        connection_item['user_name'] = user_name
        connection_item['user_id'] = user_id
        connection_item['avatar_extra'] = avatar_extra
        for p in self.pages(connection_id=connection_id):
            p['user'] = user
        if not self.connection_register.connections(olduser):
            self.drop_user(olduser)

    def refresh(self, page_id, last_user_ts=None,last_rpc_ts=None,pageProfilers=None):
        refresh_ts = datetime.now()
        page = self.page_register.refresh(page_id,last_user_ts=last_user_ts,last_rpc_ts=last_rpc_ts,refresh_ts=refresh_ts)
        if not page:
            return
        self.page_register.updatePageProfilers(page_id,pageProfilers)
        connection = self.connection_register.refresh(page['connection_id'],last_user_ts=last_user_ts,last_rpc_ts=last_rpc_ts,refresh_ts=refresh_ts)
        if not connection:
            return
        return self.user_register.refresh(connection['user'],last_user_ts=last_user_ts,last_rpc_ts=last_rpc_ts,refresh_ts=refresh_ts)


    def cleanup(self):
        if time.time()-self.last_cleanup < self.cleanup_interval:
            return
        now = datetime.now()
        for page in self.pages():
            page_max_age = self.page_max_age if not page['user'].startswith('guest_') else 40
            last_refresh_ts = page.get('last_refresh_ts') or page.get('start_ts')
            if ((now - last_refresh_ts).seconds > page_max_age):
                self.drop_page(page['register_item_id'])
        for connection in self.connections():
            last_refresh_ts = connection.get('last_refresh_ts') or  connection.get('start_ts')
            connection_max_age = self.connection_max_age if not connection['user'].startswith('guest_') else 40
            if (now - last_refresh_ts).seconds > connection_max_age:
                self.drop_connection(connection['register_item_id'],cascade=True)
        self.last_cleanup = time.time()


    def get_register(self,register_name):
        return getattr(self,'%s_register' %register_name)

    def setStoreSubscription(self,page_id,storename=None, client_path=None, active=None):
        self.page_register.setStoreSubscription(page_id,storename=storename,client_path=client_path,active=active)
            
    def subscribeTable(self,page_id,table,subscribe,subscribeMode=None):
        self.page_register.subscribeTable(page_id,table=table,subscribe=subscribe,subscribeMode=subscribeMode)

    def subscription_storechanges(self, user, page_id):
        external_datachanges = self.page_register.get_datachanges(register_item_id=page_id,reset=True)
        page_item_data = self.page_register.get_item_data(page_id)
        if not page_item_data:
            return external_datachanges
        user_subscriptions = page_item_data.getItem('_subscriptions.user')
        if not user_subscriptions:
            return external_datachanges
        store_datachanges = []
        datachanges = self.user_register.get_datachanges(user)
        user_item_data = self.user_register.get_item_data(user)
        storesubscriptions_items = user_subscriptions.items()
        global_offsets = user_item_data.getItem('_subscriptions.offsets')
        if global_offsets is None:
            global_offsets = {}
            user_item_data.setItem('_subscriptions.offsets', global_offsets)
        for j, change in enumerate(datachanges):
            changepath = change.path
            change_idx = change.change_idx
            for subpath, subdict in storesubscriptions_items:
                if subdict['on'] and changepath.startswith(subpath):
                    if change_idx > subdict.get('offset', 0):
                        subdict['offset'] = change_idx
                        change.attributes = change.attributes or {}
                        if change_idx > global_offsets.get(subpath, 0):
                            global_offsets[subpath] = change_idx
                            change.attributes['_new_datachange'] = True
                        else:
                            change.attributes.pop('_new_datachange', None)
                        store_datachanges.append(change)
        return external_datachanges+store_datachanges

    def handle_ping(self, page_id=None, reason=None, _serverstore_changes=None,**kwargs):
        _children_pages_info= kwargs.get('_children_pages_info')
        _lastUserEventTs = kwargs.get('_lastUserEventTs')
        _lastRpc = kwargs.get('_lastRpc')
        _pageProfilers = kwargs.get('_pageProfilers')
        page_item = self.refresh(page_id, _lastUserEventTs,last_rpc_ts=_lastRpc,pageProfilers=_pageProfilers)
        if not page_item:
            return False
        catalog = self.catalog
        if _serverstore_changes:
            self.set_serverstore_changes(page_id, _serverstore_changes)
        if _children_pages_info:
            for k,v in _children_pages_info.items():
                child_lastUserEventTs = v.pop('_lastUserEventTs', None)
                child_lastRpc = v.pop('_lastRpc', None)
                child_pageProfilers = v.pop('_pageProfilers', None)
                if v:
                    self.set_serverstore_changes(k, v)
                if child_lastUserEventTs:
                    child_lastUserEventTs = catalog.fromTypedText(child_lastUserEventTs)
                if child_lastRpc:
                    child_lastRpc = catalog.fromTypedText(child_lastRpc)
                self.refresh(k, child_lastUserEventTs,last_rpc_ts=child_lastRpc,pageProfilers=child_pageProfilers)
        envelope = Bag(dict(result=None))
        user=page_item['user']
        datachanges = self.handle_ping_get_datachanges(page_id, user=user)            
        if datachanges:
            envelope.setItem('dataChanges', datachanges)
        if _children_pages_info:
            for k in _children_pages_info.keys():
                datachanges = self.handle_ping_get_datachanges(k, user=user)
                if datachanges:
                    envelope.setItem('childDataChanges.%s' %k, datachanges)
        user_register_data = self.user_register.get_item_data(user)
        lastBatchUpdate = user_register_data.getItem('lastBatchUpdate')
        if lastBatchUpdate:
            if (datetime.now()-lastBatchUpdate).seconds<5:
                envelope.setItem('runningBatch',True)
            else:
                user_register_data.setItem('lastBatchUpdate',None)
        return envelope

    def handle_ping_get_datachanges(self, page_id, user=None):
        result = Bag()
        store_datachanges = self.subscription_storechanges(user,page_id)
        if store_datachanges:
            for j, change in enumerate(store_datachanges):
                result.setItem('sc_%i' % j, change.value, change_path=change.path, change_reason=change.reason,
                           change_fired=change.fired, change_attr=change.attributes,
                           change_ts=change.change_ts, change_delete=change.delete)
        return result
        
    def set_serverstore_changes(self, page_id=None, datachanges=None):
        page_item_data = self.page_register.get_item_data(page_id)
        for k, v in datachanges.items():
            page_item_data.setItem(k, self._parse_change_value(v))


    def _parse_change_value(self, change_value):
        if isinstance(change_value, basestring):
            try:
                v = self.catalog.fromTypedText(change_value)
                if isinstance(v, basestring):
                    v = v.decode('utf-8')
                return v
            except Exception, e:
                raise e
        return change_value


    def dump(self):
        """TODO"""
        with open(self.storage_path, 'w') as storagefile:
            self.user_register.dump(storagefile)
            self.connection_register.dump(storagefile)
            self.page_register.dump(storagefile)

    def load(self):
        try:
            with open(self.storage_path) as storagefile:
                self.user_register.load(storagefile)
                self.connection_register.load(storagefile)
                self.page_register.load(storagefile)
            loadedpath = self.storage_path.replace('.pik','_loaded.pik')
            if os.path.exists(loadedpath):
                os.remove(loadedpath)
            os.rename(self.storage_path,loadedpath)
            return True
        except EOFError:
            return False

    def setMaintenance(self,status,allowed_users=None):
        if status is False:
            self.allowed_users = None
            self.maintenance = False
        else:
            self.allowed_users = allowed_users
            self.maintenance = True

    def isInMaintenance(self,user=None):
        if not self.maintenance or user=='*forced*':
            return False
        if not user or not self.allowed_users:
            return self.maintenance
        return not user in self.allowed_users

    def allowedUsers(self):
        return self.allowed_users

    def __getattr__(self, fname):
        if fname=='_pyroId':
            return self._pyroId
        def decore(*args,**kwargs):
            register_name = kwargs.pop('register_name',None)
            if not register_name:
                return self.__getattribute__(fname)(*args,**kwargs)
            register = self.get_register(register_name)
            h = getattr(register,fname)
            return h(*args,**kwargs)
        return decore

        
################################### CLIENT ##########################################

class SiteRegisterClient(object):
    STORAGE_PATH = 'siteregister_data.pik'

    def __init__(self,site):
        self.site = site
        self.siteregisterserver_uri = None
        self.siteregister_uri = None
        self.storage_path = os.path.join(self.site.site_path, self.STORAGE_PATH)
        self.errors = Pyro4.errors

        daemonconfig = self.site.config.getAttr('gnrdaemon')
        daemon_uri = 'PYRO:GnrDaemon@%(host)s:%(port)s' %daemonconfig
        Pyro4.config.HMAC_KEY = str(daemonconfig['hmac_key'])
        Pyro4.config.SERIALIZER = 'pickle'
        self.gnrdaemon_proxy = Pyro4.Proxy(daemon_uri)
        
        with self.gnrdaemon_proxy as daemonProxy:
            if not self.runningDaemon(daemonProxy):
                raise Exception('GnrDaemon is not started')
            t_start = time.time()
            while not self.checkSiteRegisterServerUri(daemonProxy) and (time.time()-t_start)<2:
                pass
        print 'creating proxy',self.siteregister_uri,self.siteregisterserver_uri
        self.siteregister = Pyro4.Proxy(self.siteregister_uri)
        self.remotebag_uri =self.siteregister_uri.replace(':SiteRegister@',':RemoteData@')
        self.siteregister.setConfiguration(cleanup = self.site.custom_config.getAttr('cleanup'))


    def checkSiteRegisterServerUri(self,daemonProxy):
        if not self.siteregisterserver_uri:
            info = daemonProxy.getSite(self.site.site_name,create=True,storage_path=self.storage_path,autorestore=True)
            self.siteregisterserver_uri = info.get('server_uri',False)
            if not self.siteregisterserver_uri:
                time.sleep(1)
            else:
                self.siteregister_uri = info['register_uri']
        return self.siteregisterserver_uri

    def runningDaemon(self,daemonProxy):
        t_start = time.time()
        while (time.time()-t_start)<2:
            try:
                daemonProxy.ping()
                return True
            except Pyro4.errors.CommunicationError:
                pass
        return False


    def new_page(self, page_id, page, data=None):
        register_item = self.siteregister.new_page( page_id, pagename = page.pagename,connection_id=page.connection_id,user=page.user,
                                            user_ip=page.user_ip,user_agent=page.user_agent, data=data)
        self.add_data_to_register_item(register_item)
        return register_item

    def new_connection(self, connection_id, connection):
        register_item = self.siteregister.new_connection(connection_id,connection_name = connection.connection_name,user=connection.user,
                                                    user_id=connection.user_id,user_tags=connection.user_tags,user_ip=connection.ip,browser_name=connection.browser_name,
                                                    user_agent=connection.user_agent,avatar_extra=connection.avatar_extra)
        self.add_data_to_register_item(register_item)
        return register_item

    def pages(self,connection_id=None,user=None,index_name=None, filters=None,include_data=None):
        lazy_data = include_data=='lazy'
        if lazy_data:
            include_data=False
        pages =  self.siteregister.pages(connection_id=connection_id,user=user,index_name=index_name,filters=filters,include_data=include_data)
        #adapt for old use 
        return self.adaptListToDict(pages,lazy_data=lazy_data)

    def connections(self,user=None,include_data=None):
        lazy_data = include_data=='lazy'
        if lazy_data:
            include_data=False
        connections = self.siteregister.connections(user=user,include_data=include_data)
        return self.adaptListToDict(connections,lazy_data=lazy_data)

    def adaptListToDict(self,l,lazy_data=None):
        return dict([(c['register_item_id'],self.add_data_to_register_item(c) if lazy_data else c) for c in l])

    def users(self,include_data=None):
        lazy_data = include_data=='lazy'
        if lazy_data:
            include_data=False
        users = self.siteregister.users(include_data=include_data)
        return self.adaptListToDict(users,lazy_data=lazy_data)  

    def refresh(self,page_id, ts=None,lastRpc=None,pageProfilers=None):
        return self.siteregister.refresh(page_id,last_user_ts=ts,last_rpc_ts=lastRpc,pageProfilers=pageProfilers)

    def connectionStore(self, connection_id, triggered=False):
        return self.make_store('connection',connection_id, triggered=triggered)

    def userStore(self, user, triggered=False):
        return self.make_store('user',user, triggered=triggered)

    def pageStore(self, page_id, triggered=False):
        return self.make_store('page',page_id, triggered=triggered)

    def make_store(self, register_name,register_item_id, triggered=None):
        return ServerStore(self, register_name,register_item_id=register_item_id, triggered=triggered)

    def get_item(self,register_item_id,include_data=False,register_name=None):
        lazy_data = include_data == 'lazy'
        if include_data == 'lazy':
            include_data = False
        register_item = self.siteregister.get_item(register_item_id,include_data=include_data,register_name=register_name)
        if register_item and lazy_data:
            self.add_data_to_register_item(register_item)
        return register_item

    def add_data_to_register_item(self,register_item):
        register_item['data'] = RemoteStoreBag(self.remotebag_uri, register_item['register_name'],register_item['register_item_id'])
        return register_item

    def page(self,page_id,include_data=None):
        return self.get_item(page_id,include_data=include_data,register_name='page')

    def connection(self,connection_id,include_data=None):
        return self.get_item(connection_id,include_data=include_data,register_name='connection')

    def user(self,user,include_data=None):
        return self.get_item(user,include_data=include_data,register_name='user')

############################## TO DO #######################################

    def _debug(self,mode,name,*args,**kwargs):
        print 'external_%s' %mode,name,'ARGS',args,'KWARGS',kwargs

    def dump(self):
        """TODO"""
        self.siteregister.dump()
        print 'DUMP REGISTER %s' %self.site.site_name

    def load(self):
        result = self.siteregister.load()
        if result:
            print 'SITEREGISTER %s LOADED' %self.site.site_name
        else:
            print 'UNABLE TO LOAD REGISTER %s' %self.site.site_name

    def __getattr__(self,name):
        h = getattr(self.siteregister,name)
        if not callable(h):
            return h
        def decore(*args,**kwargs):
            return h(*args,**kwargs)
        return decore

##############################################################################

class GnrSiteRegisterServer(object):
    def __init__(self,sitename=None,daemon_uri=None,storage_path=None,debug=None):
        self.sitename = sitename
        self.gnr_daemon_uri = daemon_uri
        self.debug = debug
        self.storage_path = storage_path
        self._running = False
    
    def running(self):
        return self._running

    def run(self,autorestore=False):
        self._running = True
        if autorestore:
            self.siteregister.load()
        self.daemon.requestLoop(self.running)

    def stop(self,saveStatus=False):
        print 'stopping',saveStatus
        if saveStatus:
            print 'SAVING STATUS',self.storage_path
            self.siteregister.dump()
            print 'SAVED STATUS STATUS'
        self._running = False

    def start(self,port=None,host=None,hmac_key=None,compression=None,multiplex=None,timeout=None,polltimeout=None,autorestore=False):
        pyrokw = dict(host=host)
        if port != '*':
            pyrokw['port'] = int(port or PYRO_PORT)
        Pyro4.config.SERIALIZERS_ACCEPTED.add('pickle')
        host=host or PYRO_HOST
        hmac_key=hmac_key or PYRO_HMAC_KEY
        multiplex = multiplex or PYRO_MULTIPLEX
        Pyro4.config.HMAC_KEY = str(hmac_key)
        if compression:
            Pyro4.config.COMPRESSION = True
        if multiplex:
            Pyro4.config.SERVERTYPE = "multiplex"
        if timeout:
            Pyro4.config.TIMEOUT = timeout
        if polltimeout:
            Pyro4.config.POLLTIMEOUT = timeout
        self.daemon = Pyro4.Daemon(**pyrokw)
        self.siteregister = SiteRegister(self,sitename=self.sitename,storage_path=self.storage_path)
        autorestore = autorestore and os.path.exists(self.storage_path)
        self.main_uri = self.daemon.register(self,'SiteRegisterServer')
        print 'autorestore',autorestore,os.path.exists(self.storage_path)
        self.register_uri = self.daemon.register(self.siteregister,'SiteRegister')
        print "uri=",self.main_uri
        if self.gnr_daemon_uri:
            with Pyro4.Proxy(self.gnr_daemon_uri) as proxy:
                proxy.onRegisterStart(self.sitename,str(self.main_uri),str(self.register_uri))
        self.run(autorestore=autorestore)

########################################### SERVER STORE #######################################

class ServerStore(object):
    def __init__(self, parent,register_name=None, register_item_id=None, triggered=True,max_retry=None,retry_delay=None):
        #self.parent = parent
        self.siteregister = parent #parent.siteregister
        self.register_name = register_name
        self.register_item_id = register_item_id
        self.triggered = triggered
        self.max_retry = max_retry or LOCK_MAX_RETRY
        self.retry_delay = retry_delay or RETRY_DELAY
        self._register_item = '*'

    def __enter__(self):
        k = 0
        self.start_locking_time = time.time()
        while not self.siteregister.lock_item(self.register_item_id,register_name=self.register_name):
            time.sleep(self.retry_delay)
            k += 1
            if k>self.max_retry:
                print '************UNABLE TO LOCK STORE : %s ITEM %s ***************' % (self.register_name, self.register_item_id)
                return
        self.success_locking_time = time.time()
        return self

    def __exit__(self, type, value, tb):
        self.siteregister.unlock_item(self.register_item_id,register_name=self.register_name)
        #print 'locked',self.register_name,self.register_item_id,'time to lock',self.success_locking_time-self.start_locking_time,'locking time',time.time()-self.success_locking_time

    def reset_datachanges(self):
        return self.siteregister.reset_datachanges(self.register_item_id,register_name=self.register_name)


    def set_datachange(self, path, value=None, attributes=None, fired=False, reason=None, replace=False, delete=False):
        return self.siteregister.set_datachange(self.register_item_id,path, value=value, attributes=attributes, fired=fired,
                                                 reason=reason, replace=replace, delete=delete,register_name=self.register_name)

    def drop_datachanges(self, path):
        self.siteregister.drop_datachanges(self.register_item_id,path,register_name=self.register_name)

    def subscribe_path(self, path):
        self.siteregister.subscribe_path(self.register_item_id,path,register_name=self.register_name)

    @property
    def register_item(self):
        return self.siteregister.get_item(self.register_item_id,include_data='lazy',register_name=self.register_name)

    @property
    def data(self):
        if self.register_item:
            return self.register_item['data']
        
    @property
    def datachanges(self):
        return self.register_item['datachanges']

    @property
    def subscribed_paths(self):
        return self.register_item['subscribed_paths']

    def __getattr__(self, fname):
        if hasattr(BAG_INSTANCE, fname):
            def decore(*args,**kwargs):
                data = self.data
                if data is not None:
                    return getattr(data, fname)(*args,**kwargs)
            return decore
        else:
            raise AttributeError("register_item has no attribute '%s'" % fname)


#################################### UTILS ####################################################################


class RegisterResolver(BagResolver):
    classKwargs = {'cacheTime': 1,
                   'readOnly': False,
                   'user': None,
                   'connection_id': None,
                   '_page': None
    }
    classArgs = ['user']


    def load(self):
        if not self.user:
            return self.list_users()
        elif not self.connection_id:
            return self.list_connections(user=self.user)
        else:
            return self.list_pages(connection_id=self.connection_id)
    @property
    def register(self):
        return self._page.site.register

    def list_users(self):
        usersDict = self.register.users(include_data=True)
        result = Bag()
        for user, item_user in usersDict.items():
            item = Bag()
            data = item_user.pop('data', None)
            item_user.pop('datachanges', None)
            item_user.pop('datachanges_idx', None)
            item['info'] = Bag(item_user)
            item['data'] = data
            item.setItem('connections', RegisterResolver(user=user), cacheTime=3)
            result.setItem(user, item, user=user)
        return result

    def list_connections(self, user):
        connectionsDict = self.register.connections(user=user,include_data=True)
        result = Bag()
        for connection_id, connection in connectionsDict.items():
            delta = (datetime.now() - connection['start_ts']).seconds
            user = connection['user'] or 'Anonymous'
            connection_name = connection['connection_name']
            itemlabel = '%s (%i)' % (connection_name, delta)
            item = Bag()
            data = connection.pop('data', None)
            item['info'] = Bag(connection)
            item['data'] = data
            item.setItem('pages', RegisterResolver(user=user, connection_id=connection_id), cacheTime=2)
            result.setItem(itemlabel, item, user=user, connection_id=connection_id)
        return result

    def list_pages(self, connection_id):
        pagesDict = self.register.pages(connection_id=connection_id,include_data=True)
        result = Bag()
        for page_id, page in pagesDict.items():
            delta = (datetime.now() - page['start_ts']).seconds
            pagename = page['pagename'].replace('.py', '')
            itemlabel = '%s (%i)' % (pagename, delta)
            item = Bag()
            data = page.pop('data', None)
            item['info'] = Bag(page)
            item['data'] = data
            result.setItem(itemlabel, item, user=item['user'], connection_id=item['connection_id'], page_id=page_id)
        return result     

    def resolverSerialize(self):
        attr = super(RegisterResolver, self).resolverSerialize()
        attr['kwargs'].pop('_page',None)
        return attr


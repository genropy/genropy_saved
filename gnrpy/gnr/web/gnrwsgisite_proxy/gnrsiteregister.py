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

#------------------------------- REMOTEBAG server SIDE ---------------------------
class RemoteStoreBagHandler(object):
    def __init__(self,siteregister):
        self.siteregister = siteregister
 
    def __getattr__(self,name):
        if name=='_pyroId':
            return self._pyroId
        def decore(*args,**kwargs):
            register_name = kwargs.pop('_siteregister_register_name',None)
            register_item_id = kwargs.pop('_siteregister_register_item_id',None)
            store = self.siteregister.get_register_data(register_name,register_item_id)
            if '_pyrosubbag' in kwargs:
                _pyrosubbag = kwargs.pop('_pyrosubbag')
                store = store.getItem(_pyrosubbag)
            h = getattr(store,name)
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




class BaseRegister(object):
    """docstring for BaseRegister"""
    def __init__(self, siteregister):
        self.siteregister = siteregister
        self.registerItems = dict() 
        self.itemsData = dict()
        self.itemsTS = dict()
        self.locked_items = dict()

    def lock(self,register_item_id):
        print 'locking ',self.registerName,register_item_id,
        if not register_item_id in self.locked_items:
            self.locked_items[register_item_id] = True
            print 'ok'
            return True
        print 'failed'
        return False

    def unlock(self,register_item_id):
        print 'unlocking ',self.registerName,register_item_id
        self.locked_items.pop(register_item_id,None)

    def addRegisterItem(self,register_item,data=None):
        register_item_id = register_item['register_item_id']
        self.registerItems[register_item_id] = register_item
        self.itemsData[register_item_id] = Bag(data)


    def getRemoteData(self,register_item_id):
        pass

    def updateTS(self,register_item_id):
        self.itemsTS[register_item_id] = datetime.now()

    def get_register_data(self,register_item_id):
        return self.itemsData[register_item_id]

    def get_register_item(self,register_item_id,include_data=False):
        item = self.registerItems.get(register_item_id)
        self.updateTS(register_item_id)
        if item and include_data:
            item['data'] = self.get_register_data(register_item_id)
        return item

    def exists(self,register_item_id):
        return register_item_id in self.registerItems

    def keys(self):
        return self.registerItems.keys()

    def items(self):
        return self.registerItems.items()

    def values(self):
        return self.registerItems.values()

    def updateItem(self,register_item_id,upddict):
        item = self.registerItems.get(register_item_id)
        if not item:
            print 'missing register item ',register_item_id,self.registerName
            return 
        item.update(upddict)
        self.updateTS(register_item_id)

    def refresh(self,register_item_id,last_user_ts=None,last_rpc_ts=None,refresh_ts=None):
        item = self.registerItems.get(register_item_id)
        if not item:
            print 'missing register item ',register_item_id,self.registerName
            return 
        
        item['last_user_ts'] = max(item['last_user_ts'],last_user_ts) if item.get('last_user_ts') else last_user_ts
        item['last_rpc_ts'] = max(item['last_rpc_ts'],last_rpc_ts) if item.get('last_rpc_ts') else last_rpc_ts
        item['last_refresh_ts'] = max(item['last_refresh_ts'],refresh_ts) if item.get('last_refresh_ts') else refresh_ts
        return item

    @property
    def registerName(self):
        return self.__class__.__name__


    def dropItem(self,register_item_id):
        register_item = self.registerItems.pop(register_item_id,None)
        self.itemsData.pop(register_item_id,None)
        self.itemsTS.pop(register_item_id,None)
        return register_item



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
        self.dropItem(user)

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
        register_item = self.dropItem(register_item_id)
        if cascade:
            user = register_item['user']
            keys = self.user_connection_keys(user)
            if not keys:
                self.siteregister.drop_user(user)

    def user_connection_keys(self,user):
        return [k for k,v in self.items() if v['user'] == user]

    def user_connection_items(self,user):
        return [(k,v) for k,v in self.items() if v['user'] == user]



    def connections(self,user=None):
        connections = self.values()
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
        register_item = self.dropItem(register_item_id)
        self.pageProfilers.pop(register_item_id,None)
        if cascade:
            connection_id = register_item['connection_id']
            n = self.connection_page_keys(connection_id)
            if not n:
                self.siteregister.drop_connection(connection_id)


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

    def pages(self,connection_id=None,user=None):
        pages = self.values()
        if connection_id:
            pages = [v for v in pages if v['connection_id'] == connection_id]
        if user:
            pages = [v for v in pages if v['user'] == user]
        return pages

    def updatePageProfilers(self,page_id,pageProfilers):
        self.pageProfilers[page_id] = pageProfilers 

class SiteRegister(object):
    def __init__(self,server):
        self.server = server
        self.page_register = PageRegister(self)
        self.connection_register = ConnectionRegister(self)
        self.user_register = UserRegister(self)
        self.remotebag_handler = RemoteStoreBagHandler(self)
        self.server.daemon.register(self.remotebag_handler,'RemoteData')
        self.last_cleanup = time.time()

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


    def drop_page(self,page_id, cascade=None):
        return self.page_register.drop(page_id,cascade=cascade)   

    def drop_connection(self,connection_id,cascade=None):
        self.connection_register.drop(connection_id,cascade=cascade)

    def drop_user(self,user):
        self.user_register.drop(user)

    def user_connection_keys(self,user):
        self.connection_register.user_connection_keys(user)

    def user_connection_items(self,user):
        self.connection_register.user_connection_items(user)

    def user_connections(self,user):
        self.connection_register.user_connections(user)

    def connection_page_keys(self,connection_id):
        self.page_register.connection_page_keys(connection_id=connection_id)

    def connection_page_items(self,connection_id):
        self.page_register.connection_page_items(connection_id=connection_id)

    def connection_pages(self,connection_id):
        self.page_register.connection_pages(connection_id=connection_id)


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

    def pages(self, connection_id=None,user=None,index_name=None, filters=None):
        if index_name:
            print 'call subscribed_table_pages instead of pages'
            return self.subscribed_table_pages(index_name)
        pages = self.page_register.pages(connection_id=connection_id,user=user)
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

        for  page in pages.items():
            page = Bag(page)
            for fltname, fltval in fltdict.items():
                if checkpage(page, fltname, fltval):
                    filtered.append(page)
        return filtered

    def page(self,page_id):
        return self.page_register.get_register_item(page_id)

    def connection(self,connection_id):
        return self.connection_register.get_register_item(connection_id)

    def user(self,user):
        return self.user_register.get_register_item(user)


    def users(self,*args,**kwargs):
        return self.user_register.values()

    def connections(self,user=None):
        return self.connection_register.connections(user=user)
 

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
        self.user_register.refresh(connection['user'],last_user_ts=last_user_ts,last_rpc_ts=last_rpc_ts,refresh_ts=refresh_ts)


    def cleanup(self):
        if time.time()-self.last_cleanup < self.cleanup_interval:
            return
        now = datetime.now()
        for page in self.pages():
            last_refresh_ts = page.get('last_refresh_ts')
            if last_refresh_ts and ((now - page['last_refresh_ts']).seconds > self.page_max_age):
                self.drop_page(page['register_item_id'])

        for connection in self.connections():
            last_refresh_ts = connection.get('last_refresh_ts')
            if last_refresh_ts and ((now - connection['last_refresh_ts']).seconds > self.connection_max_age):
                self.drop_connection(connection['register_item_id'],cascade=True)
        self.last_cleanup = time.time()


    def lock_register_item(self,register_name,register_item_id):
        return self.get_register(register_name).lock(register_item_id)

    def unlock_register_item(self,register_name,register_item_id):
        return self.get_register(register_name).unlock(register_item_id)

    def get_register(self,register_name):
        return getattr(self,'%s_register' %register_name)


    def get_register_item(self,register_name,register_item_id,include_data=False):
        register = self.get_register(register_name)
        print 'register',register 
        register_item = register.get_register_item(register_item_id,include_data=include_data)
        print 'register_item',register_item
        return register_item

    def get_register_data(self,register_name,register_item_id):
        return self.get_register(register_name).get_register_data(register_item_id)



################################### CLIENT ##########################################

class SiteRegisterClient(object):
    def __init__(self,site,host=None,port=None,hmac_key=None):
        self.site = site
        host = host or PYRO_HOST
        port = port or PYRO_PORT
        hmac_key = str(hmac_key or PYRO_HMAC_KEY)
        Pyro4.config.HMAC_KEY = hmac_key
        Pyro4.config.SERIALIZER = 'pickle'
        uri = 'PYRO:SiteRegister@%s:%i' %(host,int(port))
        print 'URI',uri
        self.siteregister =  Pyro4.Proxy(uri)
        self.remotebag_uri ='PYRO:RemoteData@%s:%i' %(host,int(port))
        self.siteregister.setConfiguration(cleanup = self.site.custom_config.getAttr('cleanup'))
        #self.siteregister = SiteRegister(site)


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

    def pages(self,*args,**kwargs):
        pages =  self.siteregister.pages(*args,**kwargs)
        #adapt for old use 
        return self.adaptListToDict(pages)

    def connections(self,user=None):
        connections = self.siteregister.connections(user=user)
        return self.adaptListToDict(connections)


    def adaptListToDict(self,l):
        return dict([(c['register_item_id'],c) for c in l])

    def users(self,*args,**kwargs):
        users = self.siteregister.users(*args,**kwargs)
        #adapt for old use 
        return self.adaptListToDict(users)  

    def refresh(self,page_id, ts=None,lastRpc=None,pageProfilers=None):
        self.siteregister.refresh(page_id,last_user_ts=ts,last_rpc_ts=lastRpc,pageProfilers=pageProfilers)



    def connectionStore(self, connection_id, triggered=False):
        return self.make_store('connection',connection_id, triggered=triggered)

    def userStore(self, user, triggered=False):
        return self.make_store('user',user, triggered=triggered)

    def pageStore(self, page_id, triggered=False):
        return self.make_store('page',page_id, triggered=triggered)


    def make_store(self, register_name,register_item_id, triggered=None):
        return ServerStore(self, register_name,register_item_id=register_item_id, triggered=triggered)



    def get_register_item(self,register_name,register_item_id,include_data=False):
        lazy_data = include_data == 'lazy'
        if include_data == 'lazy':
            include_data = False
        register_item = self.siteregister.get_register_item(register_name,register_item_id,include_data=include_data)
        if lazy_data:
            self.add_data_to_register_item(register_item)
        return register_item

    def add_data_to_register_item(self,register_item):
        register_item['data'] = RemoteStoreBag(self.remotebag_uri, register_item['register_name'],register_item['register_item_id'])


############################## TO DO #######################################


    def _debug(self,mode,name,*args,**kwargs):
        print 'external_%s' %mode,name,'ARGS',args,'KWARGS',kwargs


    def __getattr__(self,name):
        h = getattr(self.siteregister,name)
        if not callable(h):
            #self._debug('property',name)
            return h
        def decore(*args,**kwargs):
            #self._debug('callable',name,*args,**kwargs)
            return h(*args,**kwargs)
        return decore


##############################################################################

class RegisterTester(object):
    """docstring for RegisterTester"""
    def __init__(self, oldregister):
        self.oldregister = oldregister
        self.newregister = SiteRegisterClient(oldregister.site)
        self.implemented = ['new_page','drop_page','page','pages',
                            'new_connection','drop_connection','connection','connections',
                            'new_user','drop_user','user','users',
                            'change_connection_user','refresh','cleanup',
                            'userStore','connectionStore','pageStore']

    def __getattr__(self,name):
        h = getattr(self.oldregister,name)
        if not name in self.implemented:
            print 'NOT IMPLEMENTED',name
            return h
        if not callable(h):
            self._debug('property',name)
            return h
        def decore(*args,**kwargs):
            newresult = getattr(self.newregister,name)(*args,**kwargs)
            #if name in ('userStore','connectionStore','pageStore'):
            #    with newresult as store:
            #        print 'testing store',args,kwargs,store
            #oldresult = h(*args,**kwargs)
            return newresult
        return decore

class PyroServer(object):
    def __init__(self,port=None,host=None,hmac_key=None,compression=None,multiplex=None,timeout=None,polltimeout=None):
        Pyro4.config.SERIALIZERS_ACCEPTED.add('pickle')
        port=port or PYRO_PORT
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
        self.daemon = Pyro4.Daemon(host=host,port=int(port))
        self.siteregister = SiteRegister(self)
        self.main_uri = self.daemon.register(self,'PyroServer')
        self.register_uri = self.daemon.register(self.siteregister,'SiteRegister')
        print "uri=",self.main_uri

    def start(self):
        self.daemon.requestLoop()

########################################### SERVER STORE #######################################

class ServerStore(object):
    def __init__(self, parent,register_name=None, register_item_id=None, triggered=True,max_retry=None,retry_delay=None):
        #self.parent = parent
        self.siteregister = parent.siteregister
        self.register_name = register_name
        self.register_item_id = register_item_id
        self.triggered = triggered
        self.max_retry = max_retry or LOCK_MAX_RETRY
        self.retry_delay = retry_delay or RETRY_DELAY
        self._register_item = '*'

    def __enter__(self):
        k = 0
        while not self.siteregister.lock_register_item(self.register_name,self.register_item_id):
            time.sleep(self.retry_delay)
            k += 1
            if k>self.max_retry:
                print '************UNABLE TO LOCK STORE : %s ITEM %s ***************' % (self.register_name, self.register_item_id)
                return
        return self

    def __exit__(self, type, value, tb):
        self.siteregister.unlock_register_item(self.register_name,self.register_item_id)
        #if tb:
        #    return
        #if not self.register_item:
        #    return
        #data = self.data
        #if data is not None:
        #    data.unsubscribe('datachanges', any=True)
        #self.parent.write(self.register_item)

    @property
    def data(self):
        """TODO"""
        if self.register_item:
            return self.register_item['data']
        else:
            return Bag()

    @property
    def register_item(self):
        """TODO"""
        if self._register_item != '*':
            return self._register_item
        self._register_item = register_item = self.siteregister.get_register_item(self.register_name,self.register_item_id,include_data='lazy')
        if not register_item:
            return
        data = register_item.get('data')
        if data is None:
            data = Bag()
            register_item['data'] = data
            register_item['datachanges'] = list()
            register_item['datachanges_idx'] = 0
            register_item['subscribed_paths'] = set()
        if self.triggered and register_item['subscribed_paths']:
            data.subscribe('datachanges', any=self._on_data_trigger)
        return register_item



    def reset_datachanges(self):
        if self.register_item:
            self.register_item['datachanges'] = list()
            self.register_item['datachanges_idx'] = 0


    def set_datachange(self, path, value=None, attributes=None, fired=False, reason=None, replace=False, delete=False):
        if not self.register_item:
            return
        datachanges = self.datachanges
        self.register_item['datachanges_idx'] = self.register_item.get('datachanges_idx', 0)
        self.register_item['datachanges_idx'] += 1
        datachange = ClientDataChange(path, value, attributes=attributes, fired=fired,
                                      reason=reason, change_idx=self.register_item['datachanges_idx'],
                                      delete=delete)
        if replace and datachange in datachanges:
            datachanges.pop(datachanges.index(datachange))
        datachanges.append(datachange)

    def drop_datachanges(self, path):
        self.datachanges[:] = [dc for dc in self.datachanges if not dc.path.startswith(path)]

    def subscribe_path(self, path):
        if self.register_item:
            self.subscribed_paths.add(path)

    def _on_data_trigger(self, node=None, ind=None, evt=None, pathlist=None, **kwargs):
        if evt == 'ins':
            pathlist.append(node.label)
        path = '.'.join(pathlist)
        for subscribed in self.subscribed_paths:
            if path.startswith(subscribed):
                self.datachanges.append(
                        ClientDataChange(path=path, value=node.value, reason='serverChange', attributes=node.attr))
                break

    def __getattr__(self, fname):
        if hasattr(BAG_INSTANCE, fname):

            return getattr(self.data, fname)
        else:
            raise AttributeError("register_item has no attribute '%s'" % fname)

    @property
    def datachanges(self):
        """TODO"""
        datachanges = []
        if self.register_item:
            datachanges = self.register_item.setdefault('datachanges', [])
        return datachanges

    @property
    def subscribed_paths(self):
        """TODO"""
        if self.register_item:
            return self.register_item['subscribed_paths']



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
        return self._page.site.register.newregister

    def list_users(self):
        usersDict = self.register.users()
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
        connectionsDict = self.register.connections(user=user)
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
        pagesDict = self.register.pages(connection_id=connection_id)
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

if __name__ == '__main__':
    s = PyroServer()
    s.start()







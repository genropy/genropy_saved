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
# 

from datetime import datetime
from gnr.core.gnrbag import Bag,BagResolver
from gnr.web.gnrwebpage import ClientDataChange
BAG_INSTANCE = Bag()
import thread
import logging 
import re
logger= logging.getLogger('gnr.web.gnrobjectregister')
from gnr.core.gnrlang import timer_call

from time import time

class ExpiredItemException(Exception):
    pass

class ServerStore(object):
    def __init__(self,parent,register_item_id=None,triggered=True):
        self.parent=parent
        self.register_item_id=register_item_id
        self.triggered = triggered    
        self._register_item = '*'  

    def __enter__(self):
        self.parent.lock_item(self.register_item_id)
        return self
        
    def __exit__(self,type,value,tb):
        self.parent.unlock_item(self.register_item_id)
        if tb:
            return
        if not self.register_item:
            return
        data = self.data
        if data is not None:
            data.unsubscribe('datachanges',any=True)
        self.parent.set_register_item(self.register_item)
        
        
    def reset_datachanges(self):
        if self.register_item:
            self.register_item['datachanges'] = list()

    def set_datachange(self,path,value,attributes=None,fired=False,reason=None,replace=False):
        datachanges = self.datachanges
        datachange = ClientDataChange(path,value,attributes=attributes,fired=fired,reason=reason)
        if replace and datachange in datachanges: 
            datachanges[datachanges.index(datachange)].update(datachange)
        else:
            datachanges.append(datachange)
    
    def subscribe_path(self,path):
        if self.register_item:
            self.subscribed_paths.add(path)
        
    def _on_data_trigger(self,node=None,ind=None,evt=None,pathlist=None,**kwargs):
        if evt == 'ins':
            pathlist.append(node.label)
        path ='.'.join(pathlist)
        for subscribed in self.subscribed_paths:
            if path.startswith(subscribed):
                self.datachanges.append(ClientDataChange(path=path,value=node.value,reason='serverChange',attributes=node.attr))
                break
                
    def __getattr__(self,fname):
        if hasattr(BAG_INSTANCE,fname):
            return getattr(self.data,fname)
        else:
            raise AttributeError("register_item has no attribute '%s'" % fname)
            
    @property
    def data(self):
        if self.register_item:
            return self.register_item['data']
        else:
            return Bag()
    
    @property
    def register_item(self):
        if self._register_item !='*':
            return self._register_item
        self._register_item = register_item = self.parent.get_register_item(self.register_item_id)
        if not register_item:
            return
        data = register_item.get('data')
        if data is None:
            data=Bag()
            register_item['data']=data
            register_item['datachanges']=list()
            register_item['subscribed_paths']=set()
        if self.triggered and register_item['subscribed_paths']:
            data.subscribe('datachanges',  any=self._on_data_trigger)
        return register_item
    
    @property
    def datachanges(self):
        datachanges=[]
        if self.register_item:
            datachanges = self.register_item.setdefault('datachanges',[])
        return datachanges
        
    @property
    def subscribed_paths(self):
        if self.register_item:
            return self.register_item['subscribed_paths']
            
class SiteRegister(object):
    def __init__(self,site):
        self.site = site
        self.sd=self.site.shared_data
        self._pages  = PageRegister(site)
        self._connections = ConnectionRegister(site)
        self._users = UserRegister(site)
        
    def new_connection(self,connection):
        #'** SITEREGISTER_new_connection: ',connection
        with  self._users as user_register:
            with  self._connections as connection_register:
                connection_register_item=connection_register._create_register_item(connection)
                connection_id=connection_register_item['register_item_id']
                assert not connection_register._exists_register_item(connection_id),'SITEREGISTER ERROR: connection_id %s already registered' % connection_id
                user=connection_register_item['user']
                user_register_item=user_register._read_register_item(user)
                if not user_register_item:
                    user_register_item=user_register._create_register_item(connection_register_item)
                user_register_item['connections'][connection_id] = connection_register_item['connection_name']
                user_register._write_register_item(user_register_item)
                connection_register._write_register_item(connection_register_item)
        return connection_register_item
        
    def change_connection_user(self,connection_id,user=None,user_tags=None,user_id=None,user_name=None):
        #print '** change_connection_user: ',connection_id
        with  self._users as user_register:
            with  self._connections as connection_register:
                connection_register_item=connection_register._read_register_item(connection_id)
                old_user = connection_register_item['user']
                old_user_register_item=user_register._read_register_item(old_user)
                old_user_register_item['connections'].pop(connection_id)
                if old_user_register_item['connections']:
                    user_register._write_register_item(old_user_register_item)
                else:
                    user_register._pop_register_item(old_user)
                    
                connection_register_item['user'] = user
                connection_register_item['user_tags'] = user_tags
                connection_register_item['user_name'] = user_name
                connection_register_item['user_id'] = user_id
                user_register_item=user_register._read_register_item(user)
                if not user_register_item:
                    user_register_item=user_register._create_register_item(connection_register_item)
                user_register_item['connections'][connection_id] = connection_register_item['connection_name']
                user_register._write_register_item(user_register_item)
                connection_register._write_register_item(connection_register_item) 
        
    def new_page(self,page,data=None):
        #print '** SITEREGISTER_new_page: ',page.page_id
        with  self._connections as connection_register:
            with self._pages as page_register:
                page_register_item = page_register._create_register_item(page,data)
                page_id = page_register_item['register_item_id']
                connection_id = page_register_item['connection_id']
                connection_register_item = connection_register._read_register_item(connection_id)
                connection_register_item['pages'][page_id] = page_register_item['pagename']
                connection_register._write_register_item(connection_register_item)
                page_register._write_register_item(page_register_item)
        return page_register_item
        
    def get_user(self,user):
        return self._users.get_register_item(user)
    
    def get_connection(self,connection_id):
        return self._connections.get_register_item(connection_id)
    
    def get_page(self,page_id):
        return self._pages.get_register_item(page_id)
        
    def drop_user():
        pass
        
    def drop_connection(self,connection_id,cascade=None):
        with  self._users as user_register:
            with  self._connections as connection_register:
                self._drop_connection(connection_id,connection_register=connection_register,user_register=user_register,cascade=cascade)
                
                
    def _drop_connection(self,connection_id,connection_register=None,user_register=None,cascade=None):
        connection_register_item = connection_register._pop_register_item(connection_id)
        if not connection_register_item:
            return
        if connection_register_item['pages']:
            for page_id in connection_register_item['pages']:
                connection_register._pop_register_item(page_id)
        user = connection_register_item['user']
        user_register_item = user_register._read_register_item(user)
        user_register_item['connections'].pop(connection_id)
        if cascade and not user_register_item['connections']:
            user_register._pop_register_item(user)
        else:
            user_register._write_register_item(user_register_item)

    def _drop_page(self,page_id,page_register=None,connection_register=None,user_register=None,cascade=None):
        page_register_item = page_register._pop_register_item(page_id)
        if not page_register_item:
            return
        connection_id = page_register_item['connection_id']
        connection_register_item = connection_register._read_register_item(connection_id)
        connection_register_item['pages'].pop(page_id)
        if cascade and not connection_register_item['pages']:
            self._drop_connection(connection_id,connection_register=connection_register,user_register=user_register,cascade=cascade)
        else:
            connection_register._write_register_item(connection_register_item)

    def drop_page(self,page_id,cascade=None):
        #print '** SITEREGISTER_drop_page: ',page_id
        with  self._connections as connection_register:
            with self._pages as page_register:
                self._drop_page(page_id,page_register,connection_register)
                
        
    def connectionStore(self,connection_id,triggered=False):
        return self._connections.make_store(connection_id,triggered=triggered)
    
    def userStore(self,user,triggered=False):
        return self._users.make_store(user,triggered=triggered)
    
    def pageStore(self,page_id,triggered=False):
        return self._pages.make_store(page_id,triggered=triggered)
    
    def refresh(self,page_id,ts=None):
        with  self._pages as page_register:
            page_register_item=page_register._read_register_item(page_id)
            if not page_register_item:
                return
            page_register._update_lastused(page_id,ts)
            
        with  self._connections as connection_register:
            connection_register._update_lastused(page_register_item['connection_id'],ts)
            
        with  self._users as user_register:
            user_register._update_lastused(page_register_item['user'],ts)
        return page_register_item
        
        
    def users(self,*args,**kwargs):
        return self._users.users(*args,**kwargs)
        
    def user_connections(self,user):
        result={}
        with  self._users as user_register:
            with  self._connections as connection_register:
                item=user_register._read_register_item(user)
                if item:
                    result = connection_register._get_multi_items(item['connections'].keys())
        return result
        
    def connection_pages(self,connection_id):
        result={}
        with  self._connections as connection_register:
            with self._pages as page_register:
                item=connection_register._read_register_item(connection_id)
                if item:
                    result = page_register._get_multi_items(item['pages'].keys())
        return result
        
    def connections(self,*args,**kwargs):
        return self._connections.connections(*args,**kwargs)
        
    def pages(self,*args,**kwargs):
        return self._pages.pages(*args,**kwargs)
        
    def tree(self):
        return PagesTreeResolver()
    
    def cleanup(self,max_age=30,cascade=False):
        with self._users as user_register:
            with self._connections as connection_register:
                with self._pages as page_register:
                    for page_id,page in self.pages().items():
                        if page['last_rpc_age']>max_age:
                            self._drop_page(page_id,page_register=page_register,
                                            connection_register=connection_register,
                                            user_register=user_register,cascade=cascade)
                    for connection_id,connection in self.connections().items():
                        if connection['last_rpc_age']>max_age:
                            self._drop_connection(connection_id,connection_register=connection_register,
                                                  user_register=user_register,cascade=cascade)
        
        
class BaseRegister(object):
    def __init__(self, site, **kwargs):
        self.site = site
        self.sd=self.site.shared_data
        self.init(**kwargs)

        
    def __enter__(self):
        self.sd.lock(self.prefix)
        return self
        
    def __exit__(self,type,value,tb):
        self.sd.unlock(self.prefix)

    def init(self, **kwargs):
        pass
    
    def make_store(self,register_item_id,triggered=None):
        return ServerStore(self,register_item_id=register_item_id,triggered=triggered)

    def _create_register_item(self, obj):
        pass 
        
    def _register_item_key(self,register_item_id):
        return '%s_ITEM_%s'%(self.prefix,register_item_id)
        
    def _lastused_key(self,register_item_id):
        return '%s_LAST_%s'%(self.prefix,register_item_id)
        
    def _update_lastused(self,register_item_id,ts=None):
        last_used_key = self._lastused_key(register_item_id)
        last_used = self.sd.get(last_used_key)
        if last_used:
            ts = max(last_used[1],ts) if ts else last_used[1]
        self.sd.set(last_used_key, (datetime.now(),ts),0)
        
    def _read_register_item(self, register_item_id):
        register_item_key = self._register_item_key(register_item_id)
        register_item=self.sd.get(register_item_key)
        if register_item:
            self._set_last_ts_in_item(register_item)
        return register_item
            
    def _exists_register_item(self, register_item_id):
        register_item_key = self._register_item_key(register_item_id)
        return self.sd.get(register_item_key) is not None
        
    def _write_register_item(self, register_item):
        """Private. It must be called only in locked mode"""
        self.log('_write_register_item',register_item=register_item)
        is_new_item = register_item.pop('_new',None)
        sd=self.sd
        register_item_id=register_item['register_item_id']
        self._set_index(register_item)
        
        sd.set(self._register_item_key(register_item_id),register_item,0)
        if is_new_item:
            self._update_lastused(register_item_id,register_item['start_ts'])
        self._on_write_register_item(register_item)
        

    def _on_write_register_item(self,register_item):
        pass
        
    def _get_index_key(self,index_name=None):
        if index_name=='*':
            ind_key='%s_MASTERINDEX'%self.prefix
        elif index_name:
            ind_key='%s_INDEX_%s'%(self.prefix,index_name)
        else:
            ind_key='%s_INDEX'%self.prefix
        return ind_key
    
    def _set_index(self,register_item,index_name=None):
        """Private. It must be called only in locked mode"""
        sd=self.sd
        register_item_id = register_item['register_item_id']
        ind_key=self._get_index_key(index_name)
        self.log('_set_index',register_item_id=register_item['register_item_id'],index_name=index_name,ind_key=ind_key)
        index=sd.get(ind_key)
        if not index:
            self.log('_set_index (create new)')
            index={}
            if index_name and index_name!='*':
                self._set_index({'register_item_id':index_name},index_name='*')
        if self.parent_index and (self.parent_index in register_item) :
            index[register_item_id]=register_item[self.parent_index]
        else:
            index[register_item_id]=True
        sd.set(ind_key,index,0)
        self.log('_set_index:writing',index=index)
        
    def _remove_index(self,register_item_id, index_name=None):
        """Private. It must be called only in locked mode"""
        sd=self.sd
        ind_key=self._get_index_key(index_name)
        index=sd.get(ind_key)
        if index:
            self.log('_remove_index',register_item_id=register_item_id,index_name=index_name,ind_key=ind_key)
            index.pop(register_item_id,None)
            self._index_rewrite(index_name,index)

    def _index_rewrite(self, index_name, index):
        """Private. It must be called only in locked mode"""
        self.log('_index_rewrite',index_name=index_name,index=index)
        sd=self.sd
        ind_key=self._get_index_key(index_name)
        if index=={}:
            if index_name and index_name!='*':
                self._remove_index(register_item_id=index_name,index_name='*')
            sd.delete(ind_key)
            self.log('_index_rewrite:index empty: deleted',ind_key=ind_key)
            return
        sd.set(ind_key,index,0)
        self.log('_index_rewrite:index updated',ind_key=ind_key)
    
    def _pop_register_item(self,register_item_id):
        """Private. It must be called only in locked mode"""
        sd=self.sd
        register_item_key=self._register_item_key(register_item_id)
        register_item=sd.get(register_item_key)
        self.log('_pop_register_item',register_item=register_item)
        sd.delete(register_item_key)
        sd.delete(self._lastused_key(register_item_id))
        self._remove_index(register_item_id)
        self._on_pop_register_item(register_item_id,register_item)
        return register_item

    def _on_pop_register_item(self, register_item_id, register_item):
        pass

    def get_register_item(self, register_item_id):
        self.log('get_register_item',register_item_id=register_item_id)
        register_item=None
        sd=self.sd
        with sd.locked(key=self.prefix):
            register_item = self._read_register_item(register_item_id)
        return register_item

    def _set_last_ts_in_item(self,register_item,last_used=None,now=None):
        now=now or datetime.now()
        def age(label):
            return (now-register_item[label]).seconds
        last_used = last_used or self.sd.get(self._lastused_key(register_item['register_item_id']))
        register_item['last_ts'],register_item['last_user_ts'] = last_used
        register_item['age'] = age('start_ts')
        register_item['last_rpc_age'] = age('last_ts')
        register_item['last_event_age'] = age('last_user_ts')

        
    def set_register_item(self,register_item):
        self.log('set_register_item',register_item=register_item)
        with self.sd.locked(self.prefix):
            self._write_register_item(register_item)

    def upd_register_item(self,register_item_id,**kwargs):
        self.log('set_register_item',register_item_id=register_item_id)
        sd=self.sd
        with sd.locked(key=self.prefix):
            register_item_key = self._register_item_key(register_item_id)
            register_item=sd.get(register_item_key)
            self.log('upd_register_item',register_item_id=register_item_id,register_item=register_item,updates=kwargs)
            if register_item:
                register_item.update(kwargs)
                self._write_register_item(register_item)
        
    def lock_item(self,register_item_id,max_retry=None,
                            lock_time=None, 
                            retry_time=None):
        return self.sd.lock(self._register_item_key(register_item_id), max_retry=max_retry,lock_time=lock_time,retry_time=retry_time)
        
    def unlock_item(self,register_item_id):
        return self.sd.unlock(self._register_item_key(register_item_id))
        
    def _register_items(self,index_name=None):
        """Registered register_items"""
        sd=self.sd
        address=self.prefix
        with sd.locked(key=address):
            index=self.sd.get(self._get_index_key(index_name)) or {}
        return self._get_multi_items(index.keys())
            
    def _get_multi_items(self,keys):
        sd=self.sd
        items=sd.get_multi(keys,'%s_ITEM_'%self.prefix)
        items_lastused=sd.get_multi(keys,'%s_LAST_'%self.prefix)
        now=datetime.now()
        for k,register_item in items.items():
            self._set_last_ts_in_item(register_item,items_lastused[k],now=now)
        return items
            
    def log(self,command,**kwargs):
        if False:
            print '-->%s:%s\n                       (%s)' % (self.name,command,str(kwargs))
        
class PageRegister(BaseRegister):
    name='page'
    prefix='PREG'
    parent_index = 'connection_id'
    
    def _create_register_item(self, page, data=None):
        register_item_id=page.page_id
        start_ts= datetime.now()
        subscribed_tables=getattr(page,'subscribed_tables',None)
        if subscribed_tables:
            subscribed_tables=subscribed_tables.split(',')
        register_item=dict(
                register_item_id=register_item_id,
                pagename=page.basename,
                connection_id=page.connection_id,
                start_ts= start_ts,
                _new=True,
                subscribed_tables=subscribed_tables or [],
                user = page.user,
                user_ip = page.user_ip,
                user_agent = page.user_agent,
                datachanges=list(),
                subscribed_paths=set()
                )
        if data:
            register_item['data'] = Bag(data)
        return register_item
    
    def _on_write_register_item(self,register_item):
        for table in register_item['subscribed_tables']:
            self._set_index(register_item,index_name=table)
     
    def _on_pop_register_item(self, register_item_id, register_item):
        for table in register_item and register_item['subscribed_tables'] or []:
            self._remove_index(register_item['register_item_id'], index_name=table)
    
    def pages(self, connection_id=None,index_name=None,filters=None):
        """returns a list of page_id and pages.
           if no index is specified all pages are returned.
           if filters return anly pages matching with filters
           filters is a string with the propname and a regex"""
        pages=self._register_items(index_name=index_name)
        if not filters:
            return pages
            
        fltdict=dict()
        for flt in filters.split(' AND '):
            fltname,fltvalue=flt.split(':',1)
            fltdict[fltname]=fltvalue
                
        filtered=dict()
        def checkpage(page,fltname,fltval):
            value=page[fltname]
            if not value:
                return
            if not isinstance(value,basestring):
                return fltval==value
            try:
                return re.match(fltval,value)
            except:
                return False
        for page_id,page in pages.items():
            page=Bag(page)
            for fltname,fltval in fltdict.items():
                if checkpage(page,fltname,fltval):
                    filtered[page_id]=page
        return filtered
                    
        
        
class ConnectionRegister(BaseRegister):
    name='connection'
    prefix='CREG'
    parent_index = 'user'

    def init(self,onAddConnection=None, onRemoveConnection=None):
        self.onAddConnection=onAddConnection
        self.onRemoveConnection=onRemoveConnection
    
    def _create_register_item(self, connection):
        register_item_id=connection.connection_id
        register_item=dict(
                register_item_id=register_item_id,
                start_ts=datetime.now(),
                _new=True,
                connection_name=connection.connection_name,
                user=connection.user,
                user_id = connection.user_id,
                user_name = connection.user_name,
                user_tags = connection.user_tags,
                user_ip=connection.ip,
                user_agent=connection.user_agent,
                browser_name=connection.browser_name,
                pages={}
                )
        return register_item
        
        
    def _on_write_register_item(self,register_item):
        pass
        

    def _on_pop_register_item(self, register_item_id, register_item):
        if hasattr(self.onRemoveConnection,'__call__'):
            self.onRemoveConnection(register_item_id)
    
    def connections(self,user=None, index_name=None):
        return self._register_items(index_name=index_name)     

class UserRegister(BaseRegister):
    name='user'
    prefix='UREG'
    parent_index = None

    def _create_register_item(self, connection_register_item):
        register_item_id= connection_register_item['user']
        register_item=dict(
                register_item_id=register_item_id,
                start_ts=datetime.now(),
                _new=True,
                user=register_item_id,
                user_id= connection_register_item['user_id'],
                user_name= connection_register_item['user_name'],
                user_tags= connection_register_item['user_tags'],
                connections={}
                )
        return register_item

    def _on_write_register_item(self,register_item):
        pass

    def _on_pop_register_item(self, register_item_id, register_item):
        pass

    def users(self, index_name=None):
        return self._register_items(index_name=index_name)
        
class PagesTreeResolver(BagResolver):
    classKwargs={'cacheTime':1,
                 'readOnly':False,
                 'user':None,
                 'connection_id':None,
                 'page':None
                 }
    classArgs=['user']
        

    def load(self): 
        if not self.user:
            return self.list_users()
        elif not self.connection_id:
            return self.list_connections(user=self.user)
        else:
            return self.list_pages(connection_id=self.connection_id)
            
    def list_users(self):
        
        usersDict = self._page.site.register.users()
        result = Bag()
        for user,item_user in usersDict.items():
            item=Bag()
            data = item_user.pop('data',None)
            connections = item_user.pop('connections')
            item['info'] = Bag([('%s:%s' %(k,str(v).replace('.','_')),v) for k,v in item_user.items()])
            item['data'] = data
            item.setItem('connections', PagesTreeResolver(user=user),cacheTime=3)
            result.setItem(user,item,user=user)
        return result 
        
    def list_connections(self,user):
        connectionsDict = self._page.site.register.user_connections(user)
        result = Bag()
        for connection_id,connection in connectionsDict.items():
            delta = (datetime.now()-connection['start_ts']).seconds
            user = connection['user'] or 'Anonymous'
            connection_name=connection['connection_name']
            itemlabel = '%s (%i)' %(connection_name,delta)
            item = Bag()
            pages = connection.pop('pages',None)
            data = connection.pop('data',None)
            item['info'] = Bag([('%s:%s' %(k,str(v).replace('.','_')),v) for k,v in connection.items()])
            item['data'] = data
            item.setItem('pages',PagesTreeResolver(user=user,connection_id=connection_id),cacheTime=2)
            result.setItem(itemlabel,item,user=user,connection_id=connection_id)
        return result 
    
    def list_pages(self,connection_id):
        pagesDict = self._page.site.register.connection_pages(connection_id)
        result = Bag()
        for page_id,page in pagesDict.items():
            delta = (datetime.now()-page['start_ts']).seconds
            pagename= page['pagename'].replace('.py','')
            itemlabel = '%s (%i)' %(pagename,delta)
            item = Bag()
            data = page.pop('data',None)
            item['info'] = Bag([('%s:%s' %(k,str(v).replace('.','_')),v) for k,v in page.items()])
            item['data'] = data
            result.setItem(itemlabel,item)
        return result     
        



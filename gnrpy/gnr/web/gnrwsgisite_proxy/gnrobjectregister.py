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
import logging 
import re
logger= logging.getLogger('gnr.web.gnrobjectregister')
from gnr.core.gnrlang import timer_call,debug_call

from time import time

    
def lock_item(func):
    def decore(self,obj,*args,**kwargs):
        key = obj if isinstance (obj,basestring) else obj['register_item_id']
        with self.locked(self.item_key(key)):
            result= func(self,obj,*args,**kwargs)
            return result
    return decore
    
def lock_page(func):
    def decore(self,key,*args,**kwargs):
        register=self.p_register
        with register.locked(register.item_key(key)):
            result= func(self,key,*args,**kwargs)
            return result
    return decore
    
def lock_connection(func):
    def decore(self,key,*args,**kwargs):
        register=self.c_register
        with register.locked(register.item_key(key)):
            result= func(self,key,*args,**kwargs)
            return result
    return decore
    
def lock_user(func):
    def decore(self,key,*args,**kwargs):
        register=self.u_register
        with register.locked(register.item_key(key)):
            result= func(self,key,*args,**kwargs)
            return result
    return decore
    
def lock_index(func):
    def decore(self,*args,**kwargs):
        index_key=self._get_index_key(index_name=kwargs.get('index_name'))
        with self.locked(index_key):
            result= func(self,*args,**kwargs)
            return result
    return decore
    
class ExpiredItemException(Exception):
    pass

class ServerStore(object):
    def __init__(self,parent,register_item_id=None,triggered=True):
        self.parent=parent
        self.register_item_id=register_item_id
        self.triggered = triggered    
        self._register_item = '*'  

    def __enter__(self):
        self.parent.lock_register_item(self.register_item_id)
        return self
        
    def __exit__(self,type,value,tb):
        self.parent.unlock_register_item(self.register_item_id)
        if tb:
            return
        if not self.register_item:
            return
        data = self.data
        if data is not None:
            data.unsubscribe('datachanges',any=True)
        self.parent.write(self.register_item)
        
        
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
        self._register_item = register_item = self.parent.read(self.register_item_id)
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
        self.p_register  = PageRegister(site)
        self.c_register = ConnectionRegister(site)
        self.u_register = UserRegister(site)
        
    @lock_connection
    def new_connection(self,connection_id,connection):
        assert not self.c_register.exists(connection_id),'SITEREGISTER ERROR: connection_id %s already registered' % connection_id
        connection_item=self.c_register.create(connection_id,connection)
        self.attach_connections_to_user(connection_item['user'],connection_item)
        self.c_register.write(connection_item)

    @lock_user
    def attach_connections_to_user(self,user,connection_items):
        if not isinstance(connection_items,list):
            connection_items=[connection_items]
        user_item=self.u_register.read(user)
        if not user_item:
            user_item=self.u_register.create(user, connection_items[0])
        for connection_item in connection_items:
            connection_id=connection_item['register_item_id'] 
            user_item['connections'][connection_id] = connection_item['connection_name']
        self.u_register.write(user_item)
        
    @lock_user
    def pop_connections_from_user(self,user,connection_items,delete_if_empty=True):
        user_item=self.u_register.read(user)
        result={}
        if not user_item:
            return
        if connection_items=='*':
            result= user_item['connections']
            user_item['connections']={}
        else:
            if not isinstance(connection_items,list):
                connection_items=[connection_items]
            for connection_item in connection_items:
                connection_id=connection_item['register_item_id'] 
                result[connection_id]=user_item['connections'].pop(connection_id,None)
        if not user_item['connections'] and delete_if_empty:
            self.u_register.pop(user)
        else: 
            self.u_register.write(user_item)
        return result
        

    def change_connection_user(self,connection_id,user=None,user_tags=None,user_id=None,user_name=None):
        connection_item=self.c_register.read(connection_id)
        connections_dict=self.pop_connections_from_user(connection_item['user'],'*',delete_if_empty=True)
        for connection_id in connections_dict.keys():
            connection_item=self.c_register.read(connection_id)
            connection_item['user'] = user
            connection_item['user_tags'] = user_tags
            connection_item['user_name'] = user_name
            connection_item['user_id'] = user_id
            self.attach_connections_to_user(connection_item['user'],connection_item)
            self.c_register.write(connection_item)

    @lock_connection
    def attach_pages_to_connection(self,connection_id,page_items):
        if not isinstance(page_items,list):
            page_items=[page_items]
        connection_item=self.c_register.read(connection_id)
        for page_item in page_items:
            page_id=page_item['register_item_id'] 
            connection_item['pages'][page_id] = page_item['pagename']
        self.c_register.write(connection_item)
    
    @lock_connection
    def pop_pages_from_connection(self,connection_id, page_items,delete_if_empty=True):
        connection_item=self.c_register.read(connection_id)
        result={}
        if not connection_item:
            return
        if page_items=='*':
            result= connection_item['pages']
            connection_item['pages']={}
        else:
            if not isinstance(page_items,list):
                page_items=[page_items]
            for page_item in page_items:
                page_id=page_item['register_item_id'] 
                result[page_id]=connection_item['pages'].pop(page_id,None)
        if not connection_item['pages'] and delete_if_empty:
            self.c_register.pop(connection_id)
        else: 
            self.c_register.write(connection_item)
        return result
        
    @lock_page
    @debug_call
    def new_page(self,page_id,page,data=None):
        page_item = self.p_register.create(page_id,page,data)
        self.attach_pages_to_connection(page_item['connection_id'],page_item)
        self.p_register.write(page_item)
        return page_item
        
    def get_user(self,user):
        return self.u_register.read(user)
    
    def connection(self,connection_id):
        return self.c_register.read(connection_id)
    
    def page(self,page_id):
        return self.p_register.read(page_id)
        
    def user(self,user):
        return self.u_register.read(user)

    def stores(self,storename):
        return
        
    @lock_connection
    #@debug_call
    def drop_connection(self,connection_id,cascade=None):
        connection_item = self.c_register.pop(connection_id)
        if not connection_item:
            return
        if connection_item['pages']:
            for page_id in connection_item['pages']:
                self.p_register.pop(page_id)
        self.pop_connections_from_user(connection_item['user'],connection_item,delete_if_empty=cascade)
        
    @lock_page
    #@debug_call
    def drop_page(self,page_id,cascade=None):
        page_item = self.p_register.pop(page_id)
        if not page_item:
            return
        self.pop_pages_from_connection(page_item['connection_id'],page_item,delete_if_empty=cascade)

    def connectionStore(self,connection_id,triggered=False):
        return self.c_register.make_store(connection_id,triggered=triggered)
    
    def userStore(self,user,triggered=False):
        return self.u_register.make_store(user,triggered=triggered)
    
    def pageStore(self,page_id,triggered=False):
        return self.p_register.make_store(page_id,triggered=triggered)
    
    def refresh(self,page_id,ts=None):
        page_item= self.p_register.read(page_id)
        if  page_item:
            self.p_register.update_lastused(page_id,ts)
            self.c_register.update_lastused(page_item['connection_id'],ts)
            self.u_register.update_lastused(page_item['user'],ts)
        return page_item
        
    def users(self,*args,**kwargs):
        return self.u_register.users(*args,**kwargs)
        
    def user_connections(self,user):
        result={}
        item=self.u_register.read(user)
        if item:
            result = self.c_register.get_multi_items(item['connections'].keys())
        return result
        
    def connection_pages(self,connection_id):
        result={}
        item=self.c_register.read(connection_id)
        if item:
            result = self.p_register.get_multi_items(item['pages'].keys())
        return result
        
    def connections(self,*args,**kwargs):
        return self.c_register.connections(*args,**kwargs)
        
    def pages(self,*args,**kwargs):
        return self.p_register.pages(*args,**kwargs)
        
    def tree(self):
        return PagesTreeResolver()
    
    def cleanup(self,max_age=30,cascade=False):
        for page_id,page in self.pages().items():
            if page['last_rpc_age']>max_age:
                self.drop_page(page_id,cascade=cascade)
        for connection_id,connection in self.connections().items():
            if connection['last_rpc_age']>max_age:
                self.drop_connection(connection_id,cascade=cascade)
    
    def cleanup_(self,max_age=30,cascade=False):
        with self.u_register as user_register:
            with self.c_register as connection_register:
                with self.p_register as page_register:
                    for page_id,page in self.pages().items():
                        if page['last_rpc_age']>max_age:
                            self.drop_page(page_id,page_register=page_register,
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

    def create(self, obj):
        pass 
        
    def item_key(self,register_item_id):
        return '%s_IT_%s'%(self.prefix,register_item_id)
        
    def lastused_key(self,register_item_id):
        return '%s_LU_%s'%(self.prefix,register_item_id)
    
    @lock_item
    #@debug_call
    def update_lastused(self,register_item_id,ts=None):
        last_used_key = self.lastused_key(register_item_id)
        last_used = self.sd.get(last_used_key)
        if last_used:
            ts = max(last_used[1],ts) if ts else last_used[1]
        self.sd.set(last_used_key, (datetime.now(),ts),0)
        
    #@debug_call
    def read(self, register_item_id):
        register_item=self.sd.get(self.item_key(register_item_id))
        if register_item:
            self._set_last_ts_in_item(register_item)
        return register_item
            
    def exists(self, register_item_id):
        return self.sd.get(self.item_key(register_item_id)) is not None
    
    @lock_item
    #@debug_call
    def write(self, register_item):
        sd=self.sd
        self.log('write',register_item=register_item)
        register_item_id=register_item['register_item_id']
        is_new_item = register_item.pop('_new',None)
        sd.set(self.item_key(register_item_id),register_item,0)
        if is_new_item:
            self.update_lastused(register_item_id,register_item['start_ts'])
        self.set_index(register_item)
        self.on_write(register_item)
        

    def on_write(self,register_item):
        pass
        
    def _get_index_key(self,index_name=None):
        if index_name=='*':
            ind_key='%s_MASTERINDEX'%self.prefix
        elif index_name:
            ind_key='%s_INDEX_%s'%(self.prefix,index_name)
        else:
            ind_key='%s_INDEX'%self.prefix
        return ind_key
        
    @lock_index
    #@debug_call
    def set_index(self,register_item,index_name=None):
        sd=self.sd
        register_item_id = register_item['register_item_id']
        ind_key=self._get_index_key(index_name)
        self.log('set_index',register_item_id=register_item['register_item_id'],index_name=index_name,ind_key=ind_key)
        index=sd.get(ind_key)
        if not index:
            self.log('set_index (create new)')
            index={}
            if index_name and index_name!='*':
                self.set_index({'register_item_id':index_name},index_name='*')
        if self.parent_index and (self.parent_index in register_item) :
            index[register_item_id]=register_item[self.parent_index]
        else:
            index[register_item_id]=True
        sd.set(ind_key,index,0)
        self.log('set_index:writing',index=index)
    
    @lock_index
    #@debug_call
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
    
    @lock_item
    #@debug_call
    def pop(self,register_item_id):
        sd=self.sd
        item_key=self.item_key(register_item_id)
        register_item=sd.get(item_key)
        self.log('pop',register_item=register_item)
        sd.delete(item_key)
        sd.delete(self.lastused_key(register_item_id))
        self._remove_index(register_item_id)
        self.on_pop(register_item_id,register_item)
        return register_item

    def on_pop(self, register_item_id, register_item):
        pass

    def _set_last_ts_in_item(self,register_item,last_used=None,now=None):
        now=now or datetime.now()
        def age(label):
            return (now-register_item[label]).seconds
        last_used = last_used or self.sd.get(self.lastused_key(register_item['register_item_id']))
        register_item['last_ts'],register_item['last_user_ts'] = last_used
        register_item['age'] = age('start_ts')
        register_item['last_rpc_age'] = age('last_ts')
        register_item['last_event_age'] = age('last_user_ts')

    @lock_item
    #@debug_call
    def upd_register_item(self,register_item_id,**kwargs):
        sd=self.sd
        self.log('set_register_item',register_item_id=register_item_id)
        item_key = self.item_key(register_item_id)
        register_item=sd.get(item_key)
        self.log('upd_register_item',register_item_id=register_item_id,register_item=register_item,updates=kwargs)
        if register_item:
            register_item.update(kwargs)
            self.write(register_item)
                
    def locked(self,key):
        return self.sd.locked(key)
        
    def lock_register_item(self,register_item_id,max_retry=None,
                            lock_time=None, 
                            retry_time=None):
        return self.sd.lock(self.item_key(register_item_id), max_retry=max_retry,lock_time=lock_time,retry_time=retry_time)
        
    def unlock_register_item(self,register_item_id):
        return self.sd.unlock(self.item_key(register_item_id))
        
    #@debug_call
    def items(self,index_name=None):
        """Registered register_items"""
        index=self.sd.get(self._get_index_key(index_name)) or {}
        return self.get_multi_items(index.keys())
        
    #@debug_call
    def get_multi_items(self,keys):
        sd=self.sd
        items=sd.get_multi(keys,'%s_IT_'%self.prefix)
        items_lastused=sd.get_multi(keys,'%s_LU_'%self.prefix)
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
    
    def create(self, page_id, page, data=None):
        register_item_id=page_id
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
    
    def on_write(self,register_item):
        for table in register_item['subscribed_tables']:
            self.set_index(register_item,index_name=table)
     
    def on_pop(self, register_item_id, register_item):
        for table in register_item and register_item['subscribed_tables'] or []:
            self._remove_index(register_item['register_item_id'], index_name=table)
    
    def pages(self, connection_id=None,index_name=None,filters=None):
        """returns a list of page_id and pages.
           if no index is specified all pages are returned.
           if filters return anly pages matching with filters
           filters is a string with the propname and a regex"""
        pages=self.items(index_name=index_name)
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
    
    def create(self, connection_id,connection):
        register_item=dict(
                register_item_id=connection_id,
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
        
        
    def on_write(self,register_item):
        pass
        

    def on_pop(self, register_item_id, register_item):
        if hasattr(self.onRemoveConnection,'__call__'):
            self.onRemoveConnection(register_item_id)
    
    def connections(self,user=None, index_name=None):
        return self.items(index_name=index_name)     

class UserRegister(BaseRegister):
    name='user'
    prefix='UREG'
    parent_index = None

    def create(self, user,connection_item):
        register_item=dict(
                register_item_id=user,
                start_ts=datetime.now(),
                _new=True,
                user=user,
                user_id= connection_item['user_id'],
                user_name= connection_item['user_name'],
                user_tags= connection_item['user_tags'],
                connections={}
                )
        return register_item

    def on_write(self,register_item):
        pass

    def on_pop(self, register_item_id, register_item):
        pass

    def users(self, index_name=None):
        return self.items(index_name=index_name)
        
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
            item_user.pop('datachanges',None)
            item_user.pop('connections')
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
            connection.pop('pages',None)
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
        



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
from gnr.core.gnrbag import Bag
from gnr.web.gnrwebpage import ClientDataChange
BAG_INSTANCE = Bag()

import logging 
import re
logger= logging.getLogger('gnr.web.gnrobjectregister')

class ExpiredItemException(Exception):
    pass


class ServerStore(object):
    def __init__(self,parent,register_item_id=None,triggered=True):
        self.parent=parent
        self.register_item_id=register_item_id
        self.triggered = triggered    
        self._register_item = '*'  

    def __enter__(self):
        self.parent.lock(self.register_item_id)
        return self
        
    def __exit__(self,type,value,tb):
        if tb:
            return
        if not self.register_item:
            return
        data = self.data
        if data is not None:
            data.unsubscribe('datachanges',any=True)
        self.parent.set_register_item(self.register_item)
        self.parent.unlock(self.register_item_id)
        
    def reset_datachanges(self):
        if self.register_item:
            self.register_item['datachanges'] = list()
    
    def add_datachange(self,path,value,**kwargs):
        datachange = ClientDataChange(path,value,**kwargs)
        self.datachanges.append(datachange)
        
    def set_datachange(self,datachange):
        datachanges = self.datachanges
        datachange = ClientDataChange(**datachange)
        if datachange in datachanges:
            datachanges[datachanges.index(datachange)].update(datachange)
        else:
            datachanges.append(datachange)
    
    def subscribe_path(self,path):
        if self.register_item:
            self.subscribed_paths.add(path)
        
    def _on_data_trigger(self,node=None,ind=None,evt=None,pathlist=None,**kwargs):
        path ='.'.join(pathlist)
        if path in self.subscribed_paths and self.register_item:
            self.datachanges.append(ClientDataChange(path=path,value=node.value,reason='serverChange'))
            
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
            register_item['data']=Bag()
            register_item['datachanges']=list()
            register_item['subscribed_paths']=set()
        if self.triggered:
            register_item['data'].subscribe('datachanges',  any=self._on_data_trigger)
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

class BaseRegister(object):
    def __init__(self, site, **kwargs):
        self.site = site
        self.sd=self.site.shared_data
        self.init(**kwargs)
    
    def init(self, **kwargs):
        pass
    
    def register(self,obj,autorenew=False):
        """Register register_item"""
        sd=self.sd
        address=self.prefix
        with sd.locked(key=address):
            register_item=self._create_register_item(obj,autorenew=autorenew)
            self._write_register_item(register_item)
            #logger.warning('registering %s' %register_item)
            
    def unregister(self,obj):
        """Unregister register_item"""
        sd=self.sd
        address=self.prefix
        register_item_id=self._create_register_item(obj)['register_item_id']
        with sd.locked(key=address):
            self._remove_register_item(register_item_id)
            #logger.warning('unregister %s' %register_item_id)

    
    def make_store(self,register_item_id,triggered=None):
        return ServerStore(self,register_item_id=register_item_id,triggered=triggered)

    def _create_register_item(self, obj,autorenew=False):
        """
        override this:
        you must return a register_item with at least
        these elements
        register_item=dict(
                register_item_id = obj.obj_id,
                timeout = obj.obj_timeout,
                refresh = obj.obj_refresh,
                renew = autorenew
                )
        """
        pass 
        
    def _register_item_key(self,register_item_id):
        return '%s_register_item_%s'%(self.prefix,register_item_id)
        
    def _expiry_key(self,register_item_id):
        return '%s_EXPIRY_%s'%(self.prefix,register_item_id)
        
    def _upd_item_expiry(self,register_item):
        self.sd.set(self._expiry_key(register_item['register_item_id']),datetime.now(),register_item['timeout'])

    def _write_register_item(self, register_item):
        """Private. It must be called only in locked mode"""
        sd=self.sd
        register_item_id=register_item['register_item_id']
        self._set_index(register_item_id)
        sd.set(self._register_item_key(register_item_id),register_item,0)
        self._upd_item_expiry(register_item)
        self._on_write_register_item(register_item)
        
   
    def _on_write_register_item(self,register_item):
        pass
        
    def _get_index_name(self,index_name=None):
        if index_name=='*':
            ind_name='%s_MASTERINDEX'%self.prefix
        elif index_name:
            ind_name='%s_INDEX_%s'%(self.prefix,index_name)
        else:
            ind_name='%s_INDEX'%self.prefix
        return ind_name
    
    def _set_index(self,register_item_id,index_name=None):
        """Private. It must be called only in locked mode"""
        sd=self.sd
        ind_name=self._get_index_name(index_name)
        index=sd.get(ind_name)
        if not index:
            index={}
            if index_name and index_name!='*':
                self._set_index(register_item_id=index_name,index_name='*')
        index[register_item_id]=True
        sd.set(ind_name,index,0)
    
    def _remove_index(self,register_item_id, index_name=None):
        """Private. It must be called only in locked mode"""
        sd=self.sd
        ind_name=self._get_index_name(index_name)
        index=sd.get(ind_name)
        if index:
            index.pop(register_item_id,None)
            self._index_rewrite(index_name,index)
            
    
    def _index_rewrite(self, index_name, index):
        """Private. It must be called only in locked mode"""
        sd=self.sd
        ind_name=self._get_index_name(index_name)
        if index=={}:
            if index_name and index_name!='*':
                self._remove_index(register_item_id=index_name,index_name='*')
            sd.delete(ind_name)
        sd.set(ind_name,index,0)
    
    def _remove_register_item(self,register_item_id):
        """Private. It must be called only in locked mode"""
        sd=self.sd
        register_item_key=self._register_item_key(register_item_id)
        register_item=sd.get(register_item_key)
        sd.delete(register_item_key)
        sd.delete(self._expiry_key(register_item_id))
        self._remove_index(register_item_id)
        self._on_remove_register_item(register_item_id,register_item)
        
    def _on_remove_register_item(self, register_item_id, register_item):
        pass
        
        
    def refresh(self,obj, renew=False):
        """Refresh register_item"""
        sd=self.sd
        address=self.prefix
        temp_register_item = self._create_register_item(obj)
        register_item_id = temp_register_item['register_item_id']
        with sd.locked(key=address):
            expiry_key=self._expiry_key(register_item_id)
            last_ts = sd.get(expiry_key) #if exists the register_item is not expired
            if last_ts:
                self._upd_item_expiry(temp_register_item)
            else:
                current_register_item=sd.get(self._register_item_key(register_item_id))
                self._tryrenew(current_register_item)
    
    def get_register_item(self, register_item_id):
        sd=self.sd
        address=self.prefix
        with sd.locked(key=address):
            register_item_key = self._register_item_key(register_item_id)
            register_item=sd.get(register_item_key)
            if not register_item:
                return
            expiry_key=self._expiry_key(register_item_id)
            last_ts = sd.get(expiry_key)
            if last_ts:
                register_item['last_ts'] = last_ts
            else:
                self._tryrenew(register_item,raise_error=True)
            return register_item
                
    def _tryrenew(self,register_item,raise_error=False):
        if register_item:
            register_item_id = register_item['register_item_id']
            if register_item.get('renew'):
                self._upd_item_expiry(register_item)
            else:
                self._remove_register_item(register_item_id)
        elif raise_error:
            raise ExpiredItemException()
    
    def set_register_item(self,register_item):
        with self.sd.locked(self.prefix):
            self._write_register_item(register_item)

    def lock(self,register_item_id,max_retry=None,
                            lock_time=None, 
                            retry_time=None):
        return self.sd.lock(self._register_item_key(register_item_id), max_retry=max_retry,lock_time=lock_time,retry_time=retry_time)
        
    def unlock(self,register_item_id):
        return self.sd.unlock(self._register_item_key(register_item_id))

    def get_index(self, index_name=None):
        sd=self.sd
        ind_name=self._get_index_name(index_name)
        address=self.prefix
        with sd.locked(key=address):
            index=sd.get(ind_name) or {}
        return index.keys()
    
    def _register_items(self,index_name=None):
        """Registered register_items"""
        sd=self.sd
        address=self.prefix
        with sd.locked(key=address):
            index=self.get_index(index_name)
            result=[]
            live_index=[register_item_address for register_item_address in sd.get_multi(index,'%s_EXPIRY_'%self.prefix) if register_item_address]
            new_index=dict([(register_item_id,True) for register_item_id in live_index])
            self._index_rewrite(index_name,new_index)
            result=sd.get_multi(live_index,'%s_register_item_'%self.prefix)
        return result
     


class PageRegister(BaseRegister):
    prefix='PREG_'
    
    def _create_register_item(self, page,autorenew=False):
        register_item_id=page.page_id
        start_ts= datetime.now()
        subscribed_tables=getattr(page,'subscribed_tables',None)
        if subscribed_tables:
            subscribed_tables=subscribed_tables.split(',')
        register_item=dict(
                register_item_id=register_item_id,
                pagename=page.basename,
                connection_id=page.connection.connection_id,
                start_ts= start_ts,
                subscribed_tables=subscribed_tables or [],
                user = page.user,
                user_ip = page.user_ip,
                user_agent = page.user_agent,
                timeout = page.page_timeout,
                refresh = page.page_refresh,
                renew=autorenew
                )
        return register_item
    
    def _on_write_register_item(self,register_item):
        for table in register_item['subscribed_tables']:
            self._set_index(register_item['register_item_id'],index_name=table)
     
    def _on_remove_register_item(self, register_item_id, register_item):
        for table in register_item and register_item['subscribed_tables'] or []:
            self._remove_index(register_item['register_item_id'], index_name=table)
    
    def pages(self, index_name=None,filters=None):
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
        def checkpage(page,fltname,fltva):
            value=page[fltname]
            if not value:
                return
            if not isinstance(value,basestring):
                return fltval==value
            try:
                return re.match(fltval,value)
            except:
                return False
        for page_id,page in pages:
            page=Bag(page)
            for fltname,fltval in fltdict:
                if checkpage(page,fltname,fltval):
                    filtered[page_id]=page
        return filtered
                    
        
        
class ConnectionRegister(BaseRegister):
    prefix='CREG_'
    
    def init(self,onAddConnection=None, onRemoveConnection=None):
        self.onAddConnection=onAddConnection
        self.onRemoveConnection=onRemoveConnection
    
    def _create_register_item(self, connection,autorenew=False):
        register_item_id=connection.connection_id
        register_item=dict(
                register_item_id=register_item_id,
                start_ts=datetime.now(),
                connection_name=connection.connection_name,
                user=connection.user,
                ip=connection.ip,
                user_agent=connection.user_agent,
                pages=connection.pages,
                timeout = connection.connection_timeout,
                refresh = connection.connection_refresh,
                renew = autorenew
                )
        return register_item
    
    def _on_write_register_item(self,register_item):
        pass
     
    def _on_remove_register_item(self, register_item_id, register_item):
        if hasattr(self.onRemoveConnection,'__call__'):
            self.onRemoveConnection(register_item_id)
        
    def connections(self, index_name=None):
        return self._register_items(index_name=index_name)     


class UserRegister(BaseRegister):
    prefix='CREG_'
    USER_TIMEOUT = 3600
    USER_REFRESH = 20

    def _create_register_item(self, user):
        page = self.db.application.site.currentPage
        connection=page.connection
        avatar=page.avatar
        
        new_user_record = dict(username=page.user,
                                        userid=avatar.userid,start_ts=datetime.now(),
                                        ip=page.request.remote_addr,
                                         user_agent=page.request.get_header('User-Agent'))
        register_item_id=page.user
        
        register_item=dict(
                register_item_id=register_item_id,
                start_ts=datetime.now(),
                cookieName=connection.cookieName,
                timeout = self.USER_TIMEOUT,
                refresh = self.USER_REFRESH
                )
        return register_item

    def _on_write_register_item(self,register_item):
        pass

    def _on_remove_register_item(self, register_item_id, register_item):
        pass

    def users(self, index_name=None):
        return self._register_items(index_name=index_name)
        

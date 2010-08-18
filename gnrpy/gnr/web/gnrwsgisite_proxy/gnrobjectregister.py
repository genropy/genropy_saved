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

class ServerStore(object):
    def __init__(self,parent,object_id,source_obj=None):
        self.parent=parent
        self.object_id=object_id
        self.locked=False
        self.source_obj=None
        if source_obj:
            self.dataFromSource(source_obj)
            
    def _get_data(self):
        if not self.source_obj:
            self.load()
        return self.source_obj['data']
    data=property(_get_data)
    
    def dataFromSource(self,source_obj=None):
        source_obj=source_obj or self.parent.get_object(self.object_id)
        data=source_obj.get('data')
        if data is None:
            data=Bag()
            source_obj['data']=data
        self.source_obj=source_obj
        
    def load(self,lock=False):
        if lock:
            self.parent.lock(self.object_id)
            self.locked=True
        self.dataFromSource()
        
    def save(self,unlock=False):
        assert self.locked,'an unlocked store cannot be saved'
        parent = self.parent
        with parent.sd.locked(parent.prefix):
            parent._set_object(self.source_obj)
        if unlock:
            parent.unlock(self.object_id)
            self.locked=False
        
    def __getattr__(self,fname):
        if hasattr(self.data,fname):
            return getattr(self.data,fname)
        else:
            raise AttributeError("object has no attribute '%s'" % fname)

class BaseRegister(object):
    
    DEFAULT_EXPIRY=60
    
    def _get_expiry(self):
        return self.DEFAULT_EXPIRY
    
    def __init__(self, site, **kwargs):
        self.site = site
        self.sd=self.site.shared_data
        self.init(**kwargs)
    
    def init(self, **kwargs):
        pass
    
    def register(self,obj):
        """Register object"""
        sd=self.sd
        address=self.prefix
        with sd.locked(key=address):
            object_info=self._get_object_info(obj)
            self._set_object(object_info)
            
    def unregister(self,obj):
        """Unregister object"""
        sd=self.sd
        address=self.prefix
        object_id=self._get_object_info(obj)['object_id']
        with sd.locked(key=address):
            self._remove_object(object_id)
    
    def _get_object_info(self, obj):
        pass
        
    def _object_key(self,object_id):
        return '%s_OBJECT_%s'%(self.prefix,object_id)
        
    def _expiry_key(self,object_id):
        return '%s_EXPIRY_%s'%(self.prefix,object_id)
        
    def _set_object(self, object_info):
        """Private. It must be called only in locked mode"""
        sd=self.sd
        object_id=object_info['object_id']
        self._set_index(object_id)
        sd.set(self._object_key(object_id),object_info,0)
        sd.set(self._expiry_key(object_id),object_id,self._get_expiry())
        self._on_set_object(object_info)
        
    def _on_set_object(self,object_info):
        pass
        
    def _get_index_name(self,index_name=None):
        if index_name=='*':
            ind_name='%s_MASTERINDEX'%self.prefix
        elif index_name:
            ind_name='%s_INDEX_%s'%(self.prefix,index_name)
        else:
            ind_name='%s_INDEX'%self.prefix
        return ind_name
    
    def _set_index(self,object_id,index_name=None):
        """Private. It must be called only in locked mode"""
        sd=self.sd
        ind_name=self._get_index_name(index_name)
        index=sd.get(ind_name)
        if not index:
            index={}
            if index_name and index_name!='*':
                self._set_index(object_id=index_name,index_name='*')
        index[object_id]=True
        sd.set(ind_name,index,0)
    
    def _remove_index(self,object_id, index_name=None):
        """Private. It must be called only in locked mode"""
        sd=self.sd
        ind_name=self._get_index_name(index_name)
        index=sd.get(ind_name)
        if index:
            index.pop(object_id,None)
            self._index_rewrite(index_name,index)
            
    
    def _index_rewrite(self, index_name, index):
        """Private. It must be called only in locked mode"""
        sd=self.sd
        ind_name=self._get_index_name(index_name)
        if index=={}:
            if index_name and index_name!='*':
                self._remove_index(object_id=index_name,index_name='*')
            sd.delete(ind_name)
        sd.set(ind_name,index,0)
    
    def _remove_object(self,object_id):
        """Private. It must be called only in locked mode"""
        sd=self.sd
        object_key=self._object_key(object_id)
        object_info=sd.get(object_key)
        sd.delete(object_key)
        sd.delete(self._expiry_key(object_id))
        self._remove_index(object_id)
        self._on_remove_object(object_id,object_info)
        
    def _on_remove_object(self, object_id, object_info):
        pass
        
        
    def refresh(self,obj, renew=False):
        """Refresh object"""
        sd=self.sd
        address=self.prefix
        object_id=self._get_object_info(obj)['object_id']
        with sd.locked(key=address):
            expiry_key=self._expiry_key(object_id)
            expiry_address = sd.get(expiry_key)
            if expiry_address:
                sd.set(expiry_key,object_id,self._get_expiry())
            elif renew:
                object_info=self._get_object_info(obj)
                self._set_object(object_info)
    
    
    def get_object(self, object_id, on_locked_object=None):
        sd=self.sd
        address=self.prefix
        with sd.locked(key=address):
            expiry_key=self._expiry_key(object_id)
            not_expired= sd.get(expiry_key)
            if not_expired:
                object_key = self._object_key(object_id)
                object_info=sd.get(object_key)
                if on_locked_object:
                    on_locked_object(object_key,object_info)
                return object_info
            else:
                self._remove_object(object_id)
    
    def on_store(self,object_id,callback):
        def cb(source_obj):
            store=ServerStore(self,object_id,source_obj)
            return callback(store)
        return self.get_object(object_id,cb) and True
        
    def lock(self,object_id,max_retry=None,
                            lock_time=None, 
                            retry_time=None):
        return self.sd.lock(self._object_key(object_id), max_retry=max_retry,lock_time=lock_time,retry_time=retry_time)
        
    def unlock(self,object_id):
        return self.sd.unlock(self._object_key(object_id))
        
    def get_store(self,object_id):
        return ServerStore(self,object_id)

    def get_index(self, index_name=None):
        sd=self.sd
        ind_name=self._get_index_name(index_name)
        address=self.prefix
        with sd.locked(key=address):
            index=sd.get(ind_name) or {}
        return index.keys()
    
    def _objects(self,index_name=None):
        """Registered objects"""
        sd=self.sd
        address=self.prefix
        with sd.locked(key=address):
            index=self.get_index(index_name)
            result=[]
            live_index=[object_address for object_address in sd.get_multi(index,'%s_EXPIRY_'%self.prefix) if object_address]
            new_index=dict([(object_id,True) for object_id in live_index])
            self._index_rewrite(index_name,new_index)
            result=sd.get_multi(live_index,'%s_OBJECT_'%self.prefix)
        return result
     


class PageRegister(BaseRegister):
    
    DEFAULT_EXPIRY=60
    prefix='PREG_'
    
    def _get_object_info(self, page):
        object_id=page.page_id
        subscribed_tables=getattr(page,'subscribed_tables',None)
        if subscribed_tables:
            subscribed_tables=subscribed_tables.split(',')
        object_info=dict(
                object_id=object_id,
                pagename=page.basename,
                connection_id=page.connection.connection_id,
                start_ts=datetime.now(),
                subscribed_tables=subscribed_tables or [],
                user = page.user,
                user_ip = page.user_ip,
                user_agent = page.user_agent
                )
        return object_info
    
    def _on_set_object(self,object_info):
        for table in object_info['subscribed_tables']:
            self._set_index(object_info['object_id'],index_name=table)
     
    def _on_remove_object(self, object_id, object_info):
        for table in object_info and object_info['subscribed_tables'] or []:
            self._remove_index(object_info['object_id'], index_name=table)
    
    def pages(self, index_name=None):
        return self._objects(index_name=index_name)
        
class ConnectionRegister(BaseRegister):
    DEFAULT_EXPIRY=3600
    prefix='CREG_'
    
    def init(self,onAddConnection=None, onRemoveConnection=None):
        self.onAddConnection=onAddConnection
        self.onRemoveConnection=onRemoveConnection
    
    def _get_expiry(self):
        return int(self.site.connection_timeout)
    
    def _get_object_info(self, connection):
        object_id=connection.connection_id
        object_info=dict(
                object_id=object_id,
                start_ts=datetime.now(),
                connection_name=connection.connection_name,
                user=connection.user,
                ip=connection.ip,
                user_agent=connection.user_agent,
                pages=connection.pages
                )
        return object_info
    
    def _on_set_object(self,object_info):
        pass
     
    def _on_remove_object(self, object_id, object_info):
        if hasattr(self.onRemoveConnection,'__call__'):
            self.onRemoveConnection(object_id)
        
    def connections(self, index_name=None):
        return self._objects(index_name=index_name)     


class UserRegister(BaseRegister):
    DEFAULT_EXPIRY=3600
    prefix='CREG_'
    
    
    
    def _get_object_info(self, user):
        page = self.db.application.site.currentPage
        connection=page.connection
        avatar=page.avatar
        
        new_connection_record = dict(username=page.user,
                                        userid=avatar.userid,start_ts=datetime.now(),
                                        ip=page.request.remote_addr,
                                         user_agent=page.request.get_header('User-Agent'))
        object_id=connection.connection_id
        
        object_info=dict(
                object_id=object_id,
                start_ts=datetime.now(),
                cookieName=connection.cookieName,
                )
        return object_info

    def _on_set_object(self,object_info):
        pass

    def _on_remove_object(self, object_id, object_info):
        pass

    def users(self, index_name=None):
        return self._objects(index_name=index_name)
        

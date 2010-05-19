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




class BaseRegister(object):
    
    DEFAULT_EXPIRY=60
    
    def __init__(self, site):
        self.site = site
        self.sd=self.site.shared_data
    
    def register(self,obj):
        """Register object"""
        sd=self.sd
        address=self.prefix
        with sd.locked(key=address):
            self._add_object(obj)
            
        
    def unregister(self,obj):
        """Unregister object"""
        sd=self.sd
        address=self.prefix
        object_id=self._get_object_info(obj)['object_id']
        with sd.locked(key=address):
            self._remove_object(object_id)
    
    def _get_object_info(self, obj):
        pass
    

    
    def _add_object(self, obj):
        sd=self.sd
        object_info=self._get_object_info(obj)
        object_id=object_info['object_id']
        self._add_index(object_id)
        sd.set('%s_OBJECT_%s'%(self.prefix,object_id),object_info,0)
        sd.set('%s_EXPIRY_%s'%(self.prefix,object_id),object_id,self.DEFAULT_EXPIRY)
        self._on_add_object(object_info)
        
    def _on_add_object(self,object_info):
        pass
        
    def _get_index_name(self,index_name=None):
        if index_name=='*':
            ind_name='%s_MASTERINDEX'%self.prefix
        elif index_name:
            ind_name='%s_INDEX_%s'%(self.prefix,index_name)
        else:
            ind_name='%s_INDEX'%self.prefix
        return ind_name
    
    def _add_index(self,object_id,index_name=None):
        sd=self.sd
        ind_name=self._get_index_name(index_name)
        index=sd.get(ind_name)
        if not index:
            index={}
            if index_name and index_name!='*':
                self._add_index(object_id=index_name,index_name='*')
        index[object_id]=True
        sd.set(ind_name,index,0)
    
    def _remove_index(self,object_id, index_name=None):
        sd=self.sd
        ind_name=self._get_index_name(index_name)
        index=sd.get(ind_name)
        if index:
            index.pop(object_id,None)
            self._index_rewrite(index_name,index)
            
    
    def _index_rewrite(self, index_name, index):
        sd=self.sd
        ind_name=self._get_index_name(index_name)
        if index=={}:
            if index_name and index_name!='*':
                self._remove_index(object_id=index_name,index_name='*')
            sd.delete(ind_name)
        sd.set(ind_name,index,0)
    
    def _remove_object(self,object_id):
        sd=self.sd
        object_info=sd.get('%s_OBJECT_%s'%(self.prefix,object_id))
        sd.delete('%s_OBJECT_%s'%(self.prefix,object_id))
        sd.delete('%s_EXPIRY_%s'%(self.prefix,object_id))
        self._remove_index(object_id)
        self._on_remove_object(object_id,object_info)
        
    def _on_remove_object(self, object_id, object_info):
        pass
        
        
    def refresh(self,obj):
        """Refresh object"""
        sd=self.sd
        address=self.prefix
        object_id=self._get_object_info(obj)['object_id']
        with sd.locked(key=address):
            object_key='%s_EXPIRY_%s'%(self.prefix,object_id)
            object_address = sd.get(object_key)
            if object_address:
                sd.set(object_key,object_id,self.DEFAULT_EXPIRY)
            else:
                self._add_object(obj)
        
    def get_object(self, object_id):
        sd=self.sd
        address=self.prefix
        with sd.locked(key=address):
            object_key='%s_EXPIRY_%s'%(self.prefix,object_id)
            read_object_id = sd.get(object_key)
            if read_object_id:
                object_info=sd.get('%s_OBJECT_%s'%(self.prefix,object_id))
                return object_info
            else:
                self._remove_object(object_id)
    
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
                subscribed_tables=subscribed_tables or []
                )
        return object_info
    
    def _on_add_object(self,object_info):
        for table in object_info['subscribed_tables']:
            self._add_index(object_info['object_id'],index_name=table)
     
    def _on_remove_object(self, object_id, object_info):
        for table in object_info and object_info['subscribed_tables'] or []:
            self._remove_index(object_info['object_id'], index_name=table)
    
    def pages(self, index_name=None):
        return self._objects(index_name=index_name)
        
class ConnectionRegister(BaseRegister):
    pass     
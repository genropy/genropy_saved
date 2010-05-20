#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  untitled
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#
import os
import datetime
import random
import time
import shutil
from gnr.core.gnrbag import Bag
from gnr.core.gnrlang import getUuid
from gnr.web.gnrwebpage_proxy.gnrbaseproxy import GnrBaseProxy




class GnrWebConnection(GnrBaseProxy):
    
    
    def init(self, **kwargs):
        self.expired = False
        self.connection_id = '_anonymous'
        self.cookie = None
        self.allConnectionsFolder = self.page.site.allConnectionsFolder
        self.user = None
        self.pages = Bag()
        self.inited=False
        
    def event_onEnd(self):
        if self.page.user:
            self._finalize()
            
    def getConnection(self, user=None):
        page = self.page
        self.ip=page.request.remote_addr
        self.user_agent=page.request.get_header('User-Agent')
        sitename = self.page.siteName
        self.connection_name = 'conn_%s'%sitename
        self.secret = page.site.config['secret'] or self.page.siteName
        self.cookie = self.page.get_cookie(self.connection_name,'marshal', secret = self.secret)
        connection_info=None
        if self.cookie:
            self.connection_id = self.cookie.value.get('connection_id')
            connection_info = page.site.connection_register.get_object(self.connection_id)
            if connection_info:
                self.user = connection_info['user']
            elif page.site.debug:
                self.user=self.cookie.value.get('user')
                page.site.connection_register.refresh(self,renew=True)
                connection_info = page.site.connection_register.get_object(self.connection_id)
        if not connection_info:
            self.user = user
            self.connection_id = getUuid()
            page.site.connection_register.register(self)
            self.cookie = self.page.newMarshalCookie(self.connection_name, {'user':self.user,'connection_id': self.connection_id, 'cookie_data':{}, 'locale':None}, secret = self.secret)
        self.inited=True
        
    def _get_data(self):
        if not hasattr(self, '_data'):
            if os.path.isfile(self.connectionFile):
                self._data = Bag(self.connectionFile)
            else:
                self._data = Bag()
                self._data['start.datetime'] = datetime.datetime.now()                
        return self._data
    data = property(_get_data)
    
        
    def _finalize(self):
        #if not self.cookie.value.get('timestamp'):
        #    self.cookie.value['timestamp'] = time.time()
        self.ip = self.page.request.remote_addr
        self.pages = Bag(self.page.session.getActivePages(self.connection_id))
        self.page.site.connection_register.refresh(self,renew=False)
        self.write()
        #self.cleanExpiredConnections(rnd=0.9)
        
    def writedata(self):
        """Write immediatly the disk file, not the cookie: use it for update data during a long process"""
        self.data.toXml(self.connectionFile, autocreate=True)

    def write(self):
        self.cookie.path = self.page.site.default_uri
        self.page.add_cookie(self.cookie)
        #self.data['cookieData'] = Bag(self.cookie.value)
        #self.data.toXml(self.connectionFile, autocreate=True)

    def _get_cookie_data(self):
        if self.cookie:
            return self.cookie.value.setdefault('cookie_data',{})
        return {}
    cookie_data = property(_get_cookie_data)
    
    def _get_locale(self):
        if self.cookie:
            return self.cookie.value.get('locale')
            
    def _set_locale(self, v):
        self.cookie.value['timestamp'] = None
        self.cookie.value['locale'] = v
    locale = property(_get_locale, _set_locale)
    
    def makeAvatar(self, avatar):
        self.cookie.value['timestamp'] = None
        cookie_data = self.cookie_data
        cookie_data['user'] = avatar.id
        cookie_data['tags'] = avatar.tags

    def _get_connectionFolder(self):
        return os.path.join(self.allConnectionsFolder, self.connection_id)
    connectionFolder = property(_get_connectionFolder)

    def _get_connectionFile(self):
        return os.path.join(self.connectionFolder, 'connection.xml')
    connectionFile = property(_get_connectionFile)
    
    def rpc_logout(self,**kwargs):
        self.close()
        
    def close(self):
        self.cookie.expires=1
        self.dropConnection(self.connection_id)
        
    def dropConnection(self,connection_id):
        page=self.page
        site=page.site
        site.connectionLog('close',connection_id=connection_id)
        site.connection_register.unregister(self)
        
    def pageFolderRemove(self):
        shutil.rmtree(os.path.join(self.connectionFolder, self.page.page_id),True)
    

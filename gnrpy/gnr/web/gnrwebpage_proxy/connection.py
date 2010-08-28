#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  untitled
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#
from gnr.core.gnrlang import getUuid
from gnr.web.gnrwebpage_proxy.gnrbaseproxy import GnrBaseProxy


CONNECTION_TIMEOUT = 3600
CONNECTION_REFRESH = 20


class GnrWebConnection(GnrBaseProxy):
    
    
    def init(self, **kwargs):
        self.expired = False
        self.connection_id = '_anonymous'
        self.cookie = None
        self.user = None
        self.inited=False
        self.ip = self.page.request.remote_addr

        self.connection_timeout = self.page.site.config('connection_timeout') or CONNECTION_TIMEOUT
        self.connection_refresh = self.page.site.config('connection_refresh') or CONNECTION_REFRESH

    def event_onEnd(self):
        if self.page.user:
            self._finalize()
            
    def getConnection(self, user=None,external_connection=None):
        page = self.page
        #self.ip=page.request.remote_addr
        self.user_agent=page.request.get_header('User-Agent')
        sitename = self.page.siteName
        self.connection_name = 'conn_%s'%sitename
        connection_info=None
        if external_connection:
            self.connection_id = external_connection
        else:
            self.secret = page.site.config['secret'] or self.page.siteName
            self.cookie = self.page.get_cookie(self.connection_name,'marshal', secret = self.secret)
            if self.cookie:
                self.connection_id = self.cookie.value.get('connection_id')            
        if self.connection_id:
            connection_info = page.site.register_connection.get_register_item(self.connection_id)
            if connection_info:
                self.user = connection_info['user']
            
        if not connection_info and user:
            self.user = user
            self.connection_id = getUuid()
            page.site.register_connection.register(self,autorenew=page.site.debug)
            self.cookie = self.page.newMarshalCookie(self.connection_name, {'user':self.user,'connection_id': self.connection_id, 'cookie_data':{}, 'locale':None}, secret = self.secret)
        self.inited=True
    
    def _finalize(self):
        self.page.site.register_connection.refresh(self)
        if self.cookie:
            self.cookie.path = self.page.site.default_uri
            self.page.add_cookie(self.cookie)        

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

    def rpc_logout(self,**kwargs):
        self.close()
        
    def close(self):
        self.cookie.expires=1
        self.dropConnection(self.connection_id)
        
    def dropConnection(self,connection_id):
        page=self.page
        site=page.site
        site.connectionLog('close',connection_id=connection_id)
        site.register_connection.unregister(self)
    

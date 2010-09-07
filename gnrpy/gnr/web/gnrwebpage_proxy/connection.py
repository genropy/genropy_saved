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

USER_AGENT_SNIFF=(('Chrome','Chrome'),
                  ('Safari','Safari'),
                  ('Firefox','Firefox'),
                  ('Opera','Opera'),
                  ('MSIE','InternetExplorer'))
                  
class GnrWebConnection(GnrBaseProxy):
    def init(self, **kwargs):
        page=self.page
        self.user_agent=page.request.get_header('User-Agent') or ''
        self.browser_name=self.sniffUserAgent()
        self.ip = self.page.request.remote_addr or '0.0.0.0'
        self.connection_name = '%s_%s'%(self.ip.replace('.','_'),self.browser_name)
        self.secret = page.site.config['secret'] or self.page.siteName
        self.cookie_name=self.page.siteName
        self.connection_id =None
        self.user=None
        self.user_tags = None
        self.user_id = None
        self.user_name = None
        self.registered_pages=[]
        self.cookie = self.read_cookie()
        self._cookie_data = None
        if self.cookie:
            self.connection_from_cookie(self.cookie.value)

    def start(self):
        if not self.connection_id:
            self.connection_id =  getUuid()
            self.user = self.guestname
            self.register()
            self.write_cookie()     
   
    def validate_page_id(self,page_id):
        assert self.connection_id,'GNRWEBPAGE: not valid connection for page_id %s  '%page_id
        return page_id in self.registered_pages

    def connection_from_cookie(self,cookie_value):
        cookie_connection_id=cookie_value.get('connection_id')
        cookie_user=cookie_value.get('user')
        cookie_data=cookie_value.get('data')
        connection_item = self.page.site.register.get_connection(cookie_connection_id)
        if connection_item:
            if (connection_item['user'] == cookie_user) and (connection_item['user_ip'] == self.page.request.remote_addr):
                self.connection_id = cookie_connection_id
                self.user = cookie_user
                self.registered_pages=connection_item['pages']
                self.user_tags = connection_item['user_tags']
                self.user_id = connection_item['user_id']
                self.user_name = connection_item['user_name']
        
    @property
    def guestname(self):
        return 'guest_%s' % self.connection_id
        
    def register(self):
        return self.page.site.register.new_connection(self)
        
    def unregister(self):
        self.page.site.register.drop_connection(self.connection_id)
        
    def upd_registration(self,user):
        pass
        
    def read_cookie(self):
        return self.page.get_cookie(self.cookie_name,'marshal', secret = self.secret)

    def write_cookie(self):
        self.cookie = self.page.newMarshalCookie(self.cookie_name, {'user':self.user,
                                                                    'connection_id': self.connection_id,
                                                                    'data':self.cookie_data,
                                                                    'locale':None}, secret = self.secret)
        self.cookie.path = self.page.site.default_uri
        self.page.add_cookie(self.cookie) 

    @property    
    def loggedUser(self):
        return (self.user != self.guestname) and self.user
        
    @property
    def cookie_data(self):
        if self._cookie_data is None:
            if self.cookie:
                self._cookie_data = self.cookie.value.get('data') or {}
            else:
                self._cookie_data ={}
        return self._cookie_data
            
        
    def sniffUserAgent(self):
        user_agent=self.user_agent
        for k,v in USER_AGENT_SNIFF:
            if k in  user_agent:
                return v
        return 'unknown browser'
    
    def _get_locale(self):
        if self.cookie:
            return self.cookie.value.get('locale')
            
    def _set_locale(self, v):
        self.cookie.value['locale'] = v
    locale = property(_get_locale, _set_locale)
        
    def change_user(self,user=None,user_tags=None,user_id=None,user_name=None):
        self.user = user or self.guestname
        self.user_tags = user_tags
        self.user_name = user_name
        self.user_id = user_id
        self.page.site.register.change_connection_user(self.connection_id,user=self.user,
                                                        user_tags=self.user_tags,user_id=self.user_id,
                                                        user_name=self.user_name)
        self.write_cookie()
        
    def rpc_logout(self):
        self.change_user()
        

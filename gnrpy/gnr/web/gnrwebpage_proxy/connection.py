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
from gnr.core.gnrbag import Bag
from gnr.core.gnrlang import getUuid
from gnr.web.gnrwebpage_proxy.gnrbaseproxy import GnrBaseProxy


CONNECTION_TIMEOUT = 3600
CONNECTION_REFRESH = 20



class GnrWebConnection(GnrBaseProxy):
    
    def init(self, **kwargs):
        self.expired = False
        
    def event_onEnd(self):
        if self.page.user:
            self._finalize()
    
    def initConnection(self):
        page = self.page
        storename = getattr(page, 'storename', None)
        sitename = self.page.siteName
        conn_name = storename and 'conn_%s_%s'%(sitename,storename) or 'conn_%s'%sitename
        self.cookieName = conn_name
        self.secret = page.site.config['secret'] or self.page.siteName
        self.allConnectionsFolder = os.path.join(self.page.siteFolder, 'data', '_connections')
        self.cookie = None
        self.oldcookie=None
        if page._user_login:
            user, password = page._user_login.split(':')
            self.connection_id = getUuid()
            avatar = page.application.getAvatar(user, password, authenticate=True,connection=self)
            self.cookie = self.page.newMarshalCookie(self.cookieName, {'connection_id': self.connection_id or getUuid(), 'slots':{}, 'locale':None, 'timestamp':None}, secret = self.secret)
            if avatar:
                self.updateAvatar(avatar)
        else:
            cookie = self.page.get_cookie(self.cookieName,'marshal', secret = self.secret)
            if cookie: #Cookie is OK
                self.oldcookie=cookie
                self.connection_id = cookie.value.get('connection_id')
                if self.connection_id:
                    cookie = self.verify(cookie)
                    if cookie:
                        self.cookie = cookie
            if not self.cookie:
                self.connection_id = getUuid()
                self.cookie = self.page.newMarshalCookie(self.cookieName, {'connection_id': self.connection_id, 'slots':{}, 'locale':None, 'timestamp':None}, secret = self.secret)

    def _get_data(self):
        if not hasattr(self, '_data'):
            if os.path.isfile(self.connectionFile):
                self._data = Bag(self.connectionFile)
            else:
                self._data = Bag()
                self._data['start.datetime'] = datetime.datetime.now()                
        return self._data
    data = property(_get_data)
    
    def cookieToRefresh(self):
        self.cookie.value['timestamp'] = None
        
    def _finalize(self):
        if not self.cookie.value.get('timestamp'):
            self.cookie.value['timestamp'] = time.time()
            self.data['ip'] = self.page.request.remote_addr
            self.data['pages'] = Bag(self.page.session.getActivePages(self.connection_id))
            self.write()
        self.cleanExpiredConnections(rnd=0.9)
        
    def writedata(self):
        """Write immediatly the disk file, not the cookie: use it for update data during a long process"""
        self.data.toXml(self.connectionFile, autocreate=True)

    def write(self):
        self.cookie.path = self.page.siteUri
        self.page.add_cookie(self.cookie)
        self.data['cookieData'] = Bag(self.cookie.value)
        self.data.toXml(self.connectionFile, autocreate=True)

    def _get_appSlot(self):
        if self.cookie:
            return self.cookie.value['slots'].setdefault(self.page.app.appId, {})
        return {}
    appSlot = property(_get_appSlot)
    
    def _get_locale(self):
        return self.cookie.value.get('locale')
    def _set_locale(self, v):
        self.cookie.value['timestamp'] = None
        self.cookie.value['locale'] = v
    locale = property(_get_locale, _set_locale)
    
    def updateAvatar(self, avatar):
        self.cookie.value['timestamp'] = None
        appSlot = self.appSlot
        appSlot['user'] = avatar.id
        appSlot['tags'] = avatar.tags

    def _get_connectionFolder(self):
        return os.path.join(self.allConnectionsFolder, self.connection_id)
    connectionFolder = property(_get_connectionFolder)

    def _get_connectionFile(self):
        return os.path.join(self.connectionFolder, 'connection.xml')
    connectionFile = property(_get_connectionFile)
    
    def rpc_logout(self,**kwargs):
        #self.cookie = self.page.newMarshalCookie(self.cookieName, {'expire':True,'connection_id': None, 'slots':{}, 'locale':None, 'timestamp':None}, secret = self.secret)
        self.close()
        
    def close(self):
        self.dropConnection(self.connection_id)
        
    def dropConnection(self,connection_id):
        self.page.site.connectionLog(self.page,'close')
        self.connFolderRemove(connection_id)
        
    def connFolderRemove(self, connection_id):
        path= os.path.join(self.allConnectionsFolder, connection_id)
        for root, dirs, files in os.walk(path, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir(path)
        
    def verify(self, cookie):
        if os.path.isfile(self.connectionFile):
            expire=False
            if cookie.value.get('expire'):
                expire=True
            elif cookie.value.get('timestamp'):
                cookieAge = time.time() - cookie.value['timestamp']
                if cookieAge < int(self.page.site.config.getItem('connection_refresh') or CONNECTION_REFRESH):
                    return cookie # fresh cookie
                elif cookieAge < int(self.page.site.config.getItem('connection_timeout') or CONNECTION_TIMEOUT):
                    cookie = self.page.newMarshalCookie(self.cookieName, {'connection_id': cookie.value.get('connection_id') or getUuid(), 
                                                                'locale':cookie.value.get('locale'),
                                                                 'slots':cookie.value.get('slots'), 'timestamp':None}, 
                                                                 secret = self.secret)
                    return cookie
                else:
                    expire=True
            if expire:
                self.isExpired = True
                #cookie = self.page.newMarshalCookie(self.cookieName, {'slots':cookie.value.get('slots'), 'timestamp':None}, secret = self.secret)
                self.close() # old cookie: destroy
                return cookie
                
    def cleanExpiredConnections(self, rnd=None):
        if (not rnd) or (random.random() > rnd):
            dirbag = self.connectionsBag()
            t = time.time()
            for conn_id, conn_files, abs_path in dirbag.digest('#k,#v,#a.abs_path'):
                try:
                    cookieAge = t - (conn_files['connection_xml.cookieData.timestamp'] or 0)
                except:
                    cookieAge = t
                if cookieAge > int(self.page.site.config.getItem('connection_timeout') or CONNECTION_TIMEOUT):
                    self.dropConnection(conn_id)
        
    def connectionsBag(self):
        if os.path.isdir(self.allConnectionsFolder):
            dirbag = Bag(self.allConnectionsFolder)['_connections']
        else:
            dirbag = Bag()
        return dirbag
            



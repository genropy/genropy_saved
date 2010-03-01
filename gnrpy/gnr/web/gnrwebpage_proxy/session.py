#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  untitled
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#
import os
import urllib
from gnr.core.gnrbag import Bag, DirectoryResolver
from gnr.core.gnrlang import optArgs
import datetime
import zipfile
import StringIO
from gnr.web.gnrwebpage_proxy.gnrbaseproxy import GnrBaseProxy

class GnrWebSession(GnrBaseProxy):
    
    def init(self, sid=None, secret=None, timeout=None, lock=None, **kwargs):
        self.page_id = self.page.page_id
        kwargs=optArgs(sid=sid, secret=secret,timeout=timeout,lock=lock)
        self.session = self.page.get_session(**kwargs)
        self.loadSessionData(False)
        self.locked = False
        self.session_changed = False
        self.session_loaded = False
        
    def loadSessionData(self, locking=True):
        if locking and not self.locked:
            if not self.session_loaded:
                self.session.load()
                self.session_loaded = True
            #self.session.lock()
            self.locked = True
        self.pagedata = self.getSessionData(self.page_id)
        self.common = self.getSessionData('common')
        
    def saveSessionData(self, persist=True):
        if not self.locked:
            raise
        self.pagedata.makePicklable()
        self.common.makePicklable()
        self.session.save()
        if persist:
            self.session.persist()
        self.session_changed = True
        #self.session.unlock()
        self.locked = False
        
    
    def getActivePages(self, connection_id):
        result = {}
        items=dict(self.session)
        if items.has_key('_accessed_time'): del items['_accessed_time']
        if items.has_key('_creation_time'): del items['_creation_time']
        for page_id, pagedata in items.items():
            if page_id != 'common' and pagedata['connection_id']==connection_id:
                result[page_id] = pagedata
        return result

    def setInPageData(self, path, value, _attributes=None, page_id=None, notifyClient=False):
        if not self.locked:
            self.loadSessionData()
        if (not page_id) or (page_id==self.page_id):
            self.pagedata.setItem(path, value, _attributes=_attributes)
        else:
            data = self.getSessionData(page_id)
            data.setItem(path, value, _attributes=_attributes)
            data.makePicklable()
            
    def modifyPageData(self, path, value, _attributes=None):
        self.loadSessionData()
        self.pagedata.setItem(path, value, _attributes=_attributes)
        self.saveSessionData()
        
    def setInCommonData(self, path, value, attr=None):
        self.common.setItem(path, value, attr)
                
    def removePageData(self):
        self.loadSessionData()
        self.session.pop(self.page_id)
        self.saveSessionData()
        
    def getSessionData(self, page_id):
        data = self.session.get(page_id)
        if data is None:
            data = Bag()
            self.session[page_id] = data
        else:
            data.restoreFromPicklable()
        return data
    
    def setSessionData(self, page_id, data):
        self.session[page_id] = data


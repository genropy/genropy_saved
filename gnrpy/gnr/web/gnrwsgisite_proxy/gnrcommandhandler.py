from __future__ import print_function

# -*- coding: utf-8 -*-

#from builtins import object
import os

class CommandHandler(object):
    def __init__(self, site):
        self.site = site
        self.db = self.site.db

    def getPending(self):
        pm = self.site.register.pendingProcessCommands()
        while pm:
            self.execute(*pm.pop(0))

    def execute(self,command,kwargs):
        handler = getattr(self,'command_%s' %command,None)
        if handler:
            kwargs = kwargs or dict()
            handler(**kwargs)

    def send(self,command,pars=None,pid=None):
        self.site.register.sendProcessCommand((command,pars),pid=pid)

    def clearTableUserConfig(self,**kwargs):
        self.send(command='clearTableUserConfig',pars=kwargs)

    def clearApplicationCache(self,key=None):
        self.send(command='clearApplicationCache',pars=dict(key=key))

    def command_clearTableUserConfig(self,pkg=None,table=None):
        if not table:
            pkglist = [pkg] if pkg else list(self.db.application.packages.keys())
            for p in pkglist:
                self.db.application.packages[p].tableBroadcast('clearUserConfiguration')
        else:
            self.db.table(table).clearUserConfiguration()

    def command_clearApplicationCache(self,key=None):
        self.site.gnrapp.cache.pop(key,None)

    def test(self,**kwargs):
        self.send(command='test',pars=kwargs)

    def command_test(self,**kwargs):
        print('test',kwargs,'pid',os.getpid())



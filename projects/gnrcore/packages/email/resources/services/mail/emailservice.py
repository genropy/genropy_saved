#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-

from gnr.core.gnrbag import Bag
from gnr.core.gnrbaseservice import GnrBaseService

class Main(GnrBaseService):
    
    def __init__(self, site, **kwargs):
        self.site = site
        self.db = site.application.db

    def getDefaultMailAccount(self):        
        mp = self._replaced_service.getDefaultMailAccount()
        if mp.get('email_account_id'):
            return self.parent.db.table('email.account').getSmtpAccountPref(mp['email_account_id'])
        return mp
    
    def sendmail(self,scheduler=None,account_id=None,moveAttachment=None,**kwargs):
        if scheduler is None:
            if account_id:
                scheduler = self.db.table('email.account').readColumns(pkey=account_id,columns='$scheduler')  
            scheduler = scheduler or self.site.getPreference('scheduler',pkg='email')
        if scheduler is True:
            if moveAttachment is None:
                moveAttachment = True
            self.db.table('email.message').newMessage(account_id=account_id,
                                                        moveAttachment=moveAttachment,**kwargs)
        else:
            self._replaced_service.sendmail(account_id=account_id,**kwargs)
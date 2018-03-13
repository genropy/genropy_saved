#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-

from gnr.core.gnrbag import Bag
from gnr.core.gnrbaseservice import GnrBaseService

class Main(GnrBaseService):
    
    def __init__(self, site, **kwargs):
        self.parent = site
        self.db = site.db

    def getDefaultMailAccount(self):        
        mp = self.parent.getService('site_mail').getDefaultMailAccount()
        if mp.get('email_account_id'):
            result =  self.db.table('email.account').getSmtpAccountPref(mp['email_account_id'])
            result['account_id'] = mp.get('email_account_id')
            return result
        return mp
    
    def sendmail(self,scheduler=None,account_id=None,moveAttachment=None,**kwargs):
        if scheduler is None:
            account_id = account_id or self.getDefaultMailAccount()['account_id']
            scheduler = self.db.table('email.account').readColumns(pkey=account_id,columns='$save_output_message')  
        if scheduler:
            if moveAttachment is None:
                moveAttachment = True
            self.db.table('email.message').newMessage(account_id=account_id,
                                                        moveAttachment=moveAttachment,**kwargs)
        else:
            self.parent.getService('site_mail').sendmail(account_id=account_id,**kwargs)
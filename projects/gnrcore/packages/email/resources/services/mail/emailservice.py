#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-

from gnr.core.gnrbag import Bag
from gnr.core.gnrbaseservice import GnrBaseService

class Main(GnrBaseService):
    
    def __init__(self, site, **kwargs):
        self.parent = site
        self.db = site.db

    def getDefaultMailAccount(self):        
        mp = self._replaced_service.getDefaultMailAccount()
        if mp.get('email_account_id'):
            result =  self.db.table('email.account').getSmtpAccountPref(mp['email_account_id'])
            result['account_id'] = mp.get('email_account_id')
            return result
        return mp
    
    def sendmail(self,save_output_message=None,account_id=None,moveAttachment=None,**kwargs):
        if save_output_message is None:
            account_id = account_id or self.getDefaultMailAccount()['account_id']
            save_output_message = self.db.table('email.account').readColumns(pkey=account_id,columns='$save_output_message')  
        if save_output_message:
            if moveAttachment is None:
                moveAttachment = True
            self.db.table('email.message').newMessage(account_id=account_id,
                                                        moveAttachment=moveAttachment,**kwargs)
        else:
            self._replaced_service.sendmail(account_id=account_id,**kwargs)
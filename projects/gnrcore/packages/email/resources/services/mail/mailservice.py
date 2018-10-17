#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-

from gnr.core.gnrbag import Bag
from gnrpkg.adm.services.mail import AdmMailService

class Service(AdmMailService):
    def getDefaultMailAccount(self):      
        mp = super(Service, self).getDefaultMailAccount()
        if mp.get('email_account_id'):
            result =  self.parent.db.table('email.account').getSmtpAccountPref(mp['email_account_id'])
            result['account_id'] = mp.get('email_account_id')
            return result
        return mp
    
    def sendmail(self,scheduler=None,account_id=None,moveAttachment=None,**kwargs):
        db = self.parent.db
        if scheduler is None:
            account_id = account_id or self.getDefaultMailAccount()['account_id']
            scheduler = db.table('email.account').readColumns(pkey=account_id,columns='$save_output_message')  
        if scheduler:
            if moveAttachment is None:
                moveAttachment = True
            db.table('email.message').newMessage(account_id=account_id,
                                                        moveAttachment=moveAttachment,**kwargs)
        else:
            super(Service, self).sendmail(account_id=account_id,**kwargs)

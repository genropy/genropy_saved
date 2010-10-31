#!/usr/bin/env python
# encoding: utf-8
"""
mail.py

Created by Francesco Porcari on 2010-10-16.
Copyright (c) 2010 Softwell. All rights reserved.
"""

from gnr.web.batch.btcbase import BaseResourceBatch
from gnr.core.gnrbag import Bag
class BaseResourceMail(BaseResourceBatch):
    def __init__(self,*args,**kwargs):
        super(BaseResourceMail,self).__init__(**kwargs)
        self.mail_handler = self.page.getService('mail')
        self.mail_preference = self.page.getUserPreference('mail',pkg='adm') or Bag(self.page.application.config.getNode('mail').attr)

        
        
    def send_one_mail(self, chunk, **kwargs):
        mp = self.mail_pars
        self.mail_handler.sendmail_template(chunk, to_address=mp['to_address'] or chunk[self.doctemplate['meta.to_address']],
                         body=self.doctemplate['content'],subject=self.doctemplate['meta.subject'],
                         cc_address=mp['cc_address'], bcc_address=mp['bcc_address'], from_address=mp['from_address'], 
                         attachments=mp['attachments'], account=mp['account'],
                         host=mp['host'], port=mp['port'], user=mp['user'], password=mp['password'],
                         ssl=mp['ssl'], tls=mp['tls'], html=True,  async=True)
    
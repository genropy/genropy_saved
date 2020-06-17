#!/usr/bin/env pythonw
# -*- coding: utf-8 -*-

from gnr.core.gnrbag import Bag
from gnr.core.gnrdecorator import extract_kwargs
from gnrpkg.adm.services.mail import AdmMailService
from gnr.web.gnrbaseclasses import BaseComponent

class Service(AdmMailService):

    def get_account_params(self, account_id=None, **kwargs):
        result = dict(self.smtp_account)
        email_account_id = account_id or self.parent.getPreference('mail.email_account_id',pkg='adm')
        if email_account_id:
            account_params =  self.parent.db.table('email.account').getSmtpAccountPref(email_account_id)
            result.update(account_params)
            result['account_id'] = email_account_id
        result.update(kwargs)
        return result

    def set_smtp_account(self, email_account_id=None,**kwargs):
        self.smtp_account = dict(email_account_id=email_account_id)
    
    @extract_kwargs(headers=True)
    def sendmail(self,scheduler=None,account_id=None,attachments=None,headers_kwargs=None,**kwargs):
        db = self.parent.db
        account_id = account_id or self.getDefaultMailAccount()['account_id']
        if scheduler is None:
            scheduler = db.table('email.account').readColumns(pkey=account_id,columns='$save_output_message')  
        if account_id:
            account_parameters = self.get_account_params(account_id)
            for k,v in account_parameters.items():
                if not kwargs.get(k,None):
                    kwargs[k]=v
        if scheduler:
            return db.table('email.message').newMessage(attachments=attachments,
                                                        headers_kwargs=headers_kwargs,**kwargs)
        else:
            kwargs['headers_kwargs'] = headers_kwargs
            return super(Service, self).sendmail(attachments=attachments,**kwargs)

class ServiceParameters(BaseComponent):
    def service_parameters(self,pane,datapath=None,**kwargs):
        fb = pane.formbuilder(datapath=datapath)
        fb.dbSelect(value='^.email_account_id',lbl='Default smtp account',dbtable='email.account')

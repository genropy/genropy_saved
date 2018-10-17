#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-

from gnr.core.gnrdecorator import extract_kwargs
from gnr.web.gnrbaseclasses import BaseComponent

from gnr.lib.services.mail import MailService


class Service(MailService):
    pass



class ServiceParameters(BaseComponent):
    def service_parameters(self,pane,datapath=None,**kwargs):
        fb = pane.formbuilder(datapath=datapath)
        fb.textbox(value='^.account_name',lbl='Account name')
        fb.textbox(value='^.from_address',lbl='From adddress')
        fb.textbox(value='^.smtp_host',lbl='Smtp host')
        fb.textbox(value='^.username',lbl='Username')
        fb.textbox(value='^.password',lbl='Password',type='password')
        fb.checkbox(value='^.ssl',label='SSL')
        fb.checkbox(value='^.tls',label='TLS')
        fb.checkbox(value='^.default',label='Default')
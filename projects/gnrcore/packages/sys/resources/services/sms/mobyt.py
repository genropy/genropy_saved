#!/usr/bin/env pythonw
# -*- coding: utf-8 -*-
#
#  untitled
#
#  Created by Giovanni Porcari on 2007-03-24 and updated by Davide Paci on 2020-06-12
#  Copyright (c) 2007-2020 Softwell. All rights reserved.
#

# --------------------------- BaseWebtool subclass ---------------------------


#MOBYT FULL DOCUMENTATION AVAILABLE HERE: https://developers.mobyt.it/?python#tpoa-api

import requests
import json
from gnr.core.gnrdecorator import public_method
from gnr.core.gnrbaseservice import GnrBaseService
from gnr.web.gnrbaseclasses import BaseComponent

class GnrCustomWebPage(object):
    py_requires='gnrcomponents/externalcall:BaseRpc'
        
    def rpc_test(self,*args,**kwargs):
        print('mobyt test args,kwargs',args,kwargs)

class Main(GnrBaseService):
    def __init__(self, parent, username=None, password=None, url=None):
        """Defines initial parameters (username and password) and API call parameters"""
        self.parent = parent
        self.username = username
        self.password = password
        self.url='https://app.mobyt.it/API/v1.0/REST'
    
    @public_method
    def getToken(self):
        """Returns user key and Access token"""
        r = requests.get('{url}/token'.format(url=self.url), 
                                params={'username':self.username, 'password':self.password})
        if r.status_code != 200:
            print("Error! http code: " + str(r.status_code) + ", body message: " + str(r.content))
        else:
            response = r.text
            user_key, Access_token = response.split(';')
            return user_key, Access_token

#LOGIN AND GETTOKEN ARE ALTERNATIVE METHODS: USE ONE OR ANOTHER IS THE SAME
#    @public_method
#    def login(self):
#        """Returns user key and session key"""
#        r = requests.get('{url}/login'.format(url=self.url), 
#                    params={'username':self.username, 'password':self.password})
#        if r.status_code != 200:
#            print("Error! http code: " + str(r.status_code) + ", body message: " + str(r.content))
#        else:
#            response = r.text            
#            user_key, session_key = response.split(';')
#            return user_key, session_key

    @public_method
    def sendsms(self, recipient=None, sender=None, message_type=None, message=None, **kwargs):
        """Sends SMS. Required parameters: 
        - user_key, Access_token / defined before
        - message type / to be defined as string (e.g message_type='N' for high quality, message_type='L' for medium quality and message_type='LL' for low cost sms)
        - message / to be defined as string, (e.g. message = 'Hello World!')
        - recipient / to be defined as string (e.g. recipient = ["+39..., +39...]")
        - sender / to be defined as string (e.g. sender = 'SenderName')"""
        user_key, access_token = self.getToken()
#        user_key, session_key = self.login()

        r = requests.post('{url}/sms'.format(url=self.url), 
                    headers={'user_key':user_key, 'Access_token':access_token, 'Content-type':'application/json'},
                    json={'message_type':message_type, 'message':message, 'recipient':recipient, 'sender':sender})
        
        if r.status_code != 201:
            print("Error! http code: " + str(r.status_code) + ", body message: " + str(r.content))
        else:
            print(r.text)


#SMS SERVICE CONFIGURATION PAGE TO INSERT USERNAME AND PASSWORD
class ServiceParameters(BaseComponent):
    def service_parameters(self,pane,datapath=None,**kwargs):
        fb = pane.formbuilder(datapath=datapath)
        fb.textbox(value='^.username',lbl='Username')
        fb.textbox(value='^.password',lbl='Password',type='password')
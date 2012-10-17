#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-

"""
 smsmessage.py

 Created by Jeff Edwards on 2012-10-15.
 Copyright (c) 2007 Softwell. All rights reserved.
"""


from gnr.core.gnrbag import Bag
# import uuid
# from datetime import datetime
import httplib2
from gnr.core.gnrbaseservice import GnrBaseService

class Main(GnrBaseService):
    
    def __init__(self, userId=None,password=None, url='http://xml.m4u.com.au',**kwargs): #
        if 'username' in kwargs:
            self.userId=kwargs['username']
        else:
            self.userId=userId
        if 'passwd' in kwargs:
            self.password=kwargs['passwd']
        else:
            self.password=password
        if 'sendername' in kwargs:
            self.sender=kwargs['sendername']
        else:
            self.sender=None
        self.url=url
        self.http = httplib2.Http()

    def checkUser(self):
        client = Bag()
        self.createHeader(client,tranType='checkUser')
        return self.sendRpc(client)

    def sendRpc(self,client):
        body = client.toXml(omitRoot=True,docHeader='XMLDATA=')
        # print body
        headers = {'Content-type': 'application/x-www-form-urlencoded'} 
        response,content=self.http.request(self.url, 'POST', headers=headers, body=body)
        result=Bag()
        result['response']=response
        result['content']=Bag(content)
        # print result
        return result

    def sendsms(self,sendMode='normal',messageFormat='SMS',receivers=None,data=None,sender=None,scheduled=None,deliveryReport=None,validityPeriod=None):
        # print 'receivers: ',type(receivers), receivers
        # print 'data: ', data
        # print 'sender: ',sender
        
        if sender:
            self.sender=sender
        client = Bag()
        self.createHeader(client,tranType='sendMessages')
        requestBody = Bag()
        recipients = Bag()
        messages = Bag()
        message = Bag()
        if type(receivers) is list or type(receivers) is tuple:
            for i,recipient in enumerate(receivers):
                count=str(i+1)
                recipients.addItem('recipient',recipient,uid=count)
        else:
            recipients.addItem('recipient',receivers,uid='1')

        if self.sender:
            message.setItem('origin',self.sender)
        message.setItem('recipients',recipients)
        if scheduled:
            message.setItem('scheduled',scheduled)
        if deliveryReport:
            message.setItem('deliveryReport',deliveryReport)
        if validityPeriod:
            message.setItem('validityPeriod',validityPeriod)
        message.setItem('content',data)
        messages.setItem('message',message,format=messageFormat,sequenceNumber='1')
        requestBody.setItem('messages',messages,sendMode=sendMode)
        client.setItem('sendMessages.requestBody',requestBody)
        return self.sendRpc(client)


    def createHeader(self,client,tranType=None):
        authenticationBag = Bag()
        authenticationBag.setItem('userId',self.userId)
        authenticationBag.setItem('password',self.password)
        client.addItem('%s.authentication' %tranType,authenticationBag)
        client.setAttr(tranType,xmlns="http://xml.m4u.com.au/2009")


if __name__ == '__main__':
    sp = Main(userId='SoftwellPtyLt003',password='p8DDMP6T')
    #print sp.checkUser()
    print sp.sendsms(receivers='61411232239',data='This is a message for you from Jeffs code')#61423373242
    #print sp.sendsms(receivers=['39335290194','393386611042'],data='This is a message for you from Jeffs code')
    #print sp.sendsms(receivers=['61411232239'],data='This is a message for you from Jeffs code')
    
    # self.getService('sms').sendsms(receivers='mobile str or list',data=message) # sender='phonenumber' is optional
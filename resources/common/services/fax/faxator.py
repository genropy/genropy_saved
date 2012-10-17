#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  untitled
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#

# --------------------------- BaseWebtool subclass ---------------------------


from gnr.core.gnrbaseservice import GnrBaseService
from gnr.core.gnrlang import getUuid

class Main(GnrBaseService):
    def __init__(self, parent, username=None, password=None,address=None,attachment=None,
                    mail_smtp_host=None,mail_port=None,mail_from_address=None,mail_tls=None,mail_ssl=None,mail_user=None,mail_password=None):
        self.parent = parent
        self.username = username
        self.password = password
        self.address = address or 'fax@faxator.com'
        self.attachment = self.parent.getStaticPath('site:%s' %attachment)
        self.mailhandler = self.parent.getService('mail')
        self.mail_pars = dict(smtp_host=mail_smtp_host,user=mail_user,password=mail_password,
                                from_address=mail_from_address,tls=mail_tls,ssl=mail_ssl,port=mail_port)

    def sendfax(self,receivers=None,message=None,filepath=None,**kwargs):
        if message:
            message = '{\\rtf %s}' %message.replace('\n','\par')
            filepath = self.parent.getStaticPath('page:temp','%s.rtf' %getUuid(),autocreate=-1)
            with open(filepath,'w') as f:
                f.write(message)
        subject = receivers.replace('+39','').replace(' ','').replace('/','').replace('+','')
        #receivers = receivers.replace(' ','').replace('/','').replace(',','\n')
        #rec_path = self.parent.getStaticPath('page:temp','%s.txt' %getUuid(),autocreate=-1)
        #with open(rec_path, 'w') as f:
        #    f.write(receivers)
        self.mailhandler.sendmail(to_address=self.address,attachments=[filepath,(self.attachment,'text/text')],body='',subject=subject,
                                **self.mail_pars)


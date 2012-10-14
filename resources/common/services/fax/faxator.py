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
    def __init__(self, parent, username=None, password=None,address=None,attachment=None):
        self.parent = parent
        self.username = username
        self.password = password
        self.address = address or 'fax@faxator.com'
        self.attachment = attachment
        self.mailhandler = self.parent.getService('mail')

    def sendfax(self,receivers=None,message=None,filepath=None,**kwargs):
        if message:
            message = '{\\rtf %s}' %message.replace('\n','\par')
            filepath = self.parent.getStaticPath('page:temp','%s.rtf' %getUuid(),autocreate=-1)
            with open(filepath,'w') as f:
                f.write(message)
        receivers = receivers.replace(' ','').replace('/','').replace(',','\n')
        rec_path = self.parent.getStaticPath('page:temp','%s.txt' %getUuid(),autocreate=-1)
        with open(rec_path, 'w') as f:
            f.write(receivers)
        self.mailhandler.sendmail(to_address=self.address,attachments=[rec_path,filepath,self.attachment],body='',subject='')


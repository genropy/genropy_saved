#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  Created by Saverio Porcari on 2013-04-06.
#  Copyright (c) 2013 Softwell. All rights reserved.


from gnr.core.gnrbaseservice import GnrBaseService                                                  
import urllib2
import os
from gnr.core.gnrbag import NetBag
from gnr.core.gnrlang import GnrDebugException


class Main(GnrBaseService):
    def __init__(self,parent,**kwargs):
        self.parent = parent

    def __call__(self,fullpath=None):
        platform = fullpath.split(os.path.sep)[-2]
        service_url = 'http://services.genropy.net/electron/electron'
        electron_pars = self.parent.config.getAttr('electron') or {}
        name = electron_pars.get('name') or self.parent.site_name
        url = self.parent.external_host
        result = NetBag(service_url,'make_electron' , name=name, platform=platform,app_url=url,recreate=True)
        dlurl = 'http://services.genropy.net%s' %result()['result']
        self.parent.getService('download')(dlurl,filepath=fullpath)


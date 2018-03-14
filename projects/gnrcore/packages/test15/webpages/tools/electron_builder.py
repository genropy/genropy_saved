# -*- coding: UTF-8 -*-

# dataremote.py
# Created by Francesco Porcari on 2010-10-29.
# Copyright (c) 2010 Softwell. All rights reserved.

"""dataRemote"""

import datetime
from gnr.core.gnrdecorator import public_method
from gnr.core.gnrbag import NetBag

class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerFull"
    
    def test_1_makebuilder(self, pane):
        pane.button('Download electron app',
                    action='FIRE .download_electron')
        pane.dataRpc(None,self.download_electron,_fired='^.download_electron',_lockScreen=True)
    
    @public_method
    def download_electron(self,):
        platform = {'windows':'windows','linux':'linux','mac':'osx'}.get(self.connection.user_device.split(':')[0])
        if not platform:
            return
        service_url = 'http://services.genropy.net/electron/electron'
        electron_pars = self.site.config.getAttr('electron') or {}
        name = electron_pars.get('name') or self.site.site_name
        url = self.request.host_url
        result = NetBag(service_url,'make_electron' , name=name, platform=platform,app_url=url)
        dlurl = 'http://services.genropy.net%s' %result()['result']
        self.setInClientData('gnr.downloadurl',dlurl)
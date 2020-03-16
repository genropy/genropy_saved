#!/usr/bin/env pythonw
# -*- coding: utf-8 -*-
#
#  Created by Saverio Porcari on 2013-04-06.
#  Copyright (c) 2013 Softwell. All rights reserved.

from gnr.app.gnrconfig import gnrConfigPath,getRmsOptions

from gnr.lib.services import GnrBaseService
from gnr.core.gnrbag import NetBag
from gnr.web.gnrbaseclasses import BaseComponent


class Main(GnrBaseService):
    def __init__(self, parent=None,token=None,domain=None,host=None,**kwargs):
        self.parent = parent
        self.token = token
        self.host = host
        self.domain = domain
        self.rms = getRmsOptions()
        #service_name = instancename

    def authenticatedUrl(self):
        return self.parent.dummyPage.dev.authenticatedUrl(self.rms['url'],
                                                        user='gnrtoken',
                                                        password=self.rms['token'])

    def registerInstance(self):
        url = self.authenticatedUrl()
        result =  NetBag(url,'register_instance',code=self.service_name,
                            token=self.token,
                            domain=self.domain,
                            pod_token=self.rms['token'])()
        

    def pingHost(self):
        pass
    

class ServiceParameters(BaseComponent):

    def service_parameters(self,pane,datapath=None,**kwargs):
        fb = pane.formbuilder(datapath=datapath)
        fb.textbox(value='^.domain',lbl='Domain')
        fb.textbox(value='^.host',lbl='Host')
        fb.textbox(value='^.token',lbl='Token',readOnly=True,_tags='_DEV_')

        #fb.textbox(value='^.pod_token',lbl='Pod Token',_tags='_DEV_')
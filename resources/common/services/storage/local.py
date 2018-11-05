#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-


from gnr.lib.services.storage import BaseLocalService
from gnr.web.gnrbaseclasses import BaseComponent

class Service(BaseLocalService):
    pass

class ServiceParameters(BaseComponent):

    def service_parameters(self,pane,datapath=None,**kwargs):
        fb = pane.formbuilder(datapath=datapath)
        fb.textbox(value='^.base_path',lbl='Base path')
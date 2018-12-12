#!/usr/bin/env pythonw
# -*- coding: utf-8 -*-


from gnr.lib.services.storage import BaseLocalService
from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method
from gnr.core.gnrbag import Bag

class Service(BaseLocalService):
    pass

class ServiceParameters(BaseComponent):
    py_requires = 'gnrcomponents/storagetree:StorageTree'
    def service_parameters(self,pane,datapath=None,**kwargs):
        bc = pane.borderContainer()
        fb = bc.contentPane(region='top').formbuilder(datapath=datapath)
        fb.textbox(value='^.base_path',lbl='Base path')
        bc.storageTreeFrame(frameCode='localStorage',storagepath='^#FORM.record.service_name?=#v+":"',
                                border='1px solid silver',margin='2px',rounded=4,
                                region='center',preview_region='right',
                                store__onBuilt=True,
                                preview_border_left='1px solid silver',preview_width='50%')
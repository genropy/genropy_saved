#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-


from gnr.lib.services.storage import BaseLocalService,StorageResolver
from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method
from gnr.core.gnrbag import Bag

class Service(BaseLocalService):
    pass

class ServiceParameters(BaseComponent):

    def service_parameters(self,pane,datapath=None,**kwargs):
        bc = pane.borderContainer()
        fb = bc.contentPane(region='top').formbuilder(datapath=datapath)
        fb.textbox(value='^.base_path',lbl='Base path')
        center = bc.contentPane(region='center',_workspace=True,nodeId='storage_tree_local')
        center.dataRpc('#WORKSPACE.store',self.getStorageRes,
                    storage_name='^#FORM.record.service_name',_if='storage_name',
                    _else='return new gnr.GnrBag();')
        center.tree(storepath='#WORKSPACE.store', hideValues=True)

    @public_method
    def getStorageRes(self,storage_name=None):
        result = Bag()
        result.setItem('root',StorageResolver('%s:' %storage_name,cacheTime=10,
                                                dropext=True,readOnly=False, _page=self)())
        return result

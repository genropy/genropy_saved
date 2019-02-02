#!/usr/bin/env pythonw
# -*- coding: utf-8 -*-

from gnr.lib.services.storage import StorageService,GnrBaseService
from gnr.web.gnrbaseclasses import BaseComponent
import types

class Service(StorageService):

    def __init__(self, parent=None, relative_path=None, parent_service=None,**kwargs):
        dir_base = dir(GnrBaseService)
        for attr in dir(StorageService):
            if not attr in dir_base:
                delattr(self, attr)
        self.parent = parent
        self.parent_service =  self.parent.getService('storage',parent_service)
        self.parent_path = self.parent_service.base_path
        self.relative_path = relative_path
        self.__class__ = self.parent_service.__class__


    @property
    def _resolved_relative(self):
        #resolve dbstore...
        return self.relative_path

    @property
    def base_path(self):
        return '%s/%s'%(self.parent_path, self._resolved_relative) if self.parent_path else self._resolved_relative

    def __getattr__(self, name):
        if name in self.__dict__:
            return getattr(self, name)
        else:
            parent_attr = getattr(self.parent_service, name)
            if callable(parent_attr):
                parent_attr = types.MethodType(parent_attr.__func__, self, self.__class__)
            self.__dict__[name] = parent_attr
            return parent_attr
    


class ServiceParameters(BaseComponent):
    py_requires = 'gnrcomponents/storagetree:StorageTree'
    def service_parameters(self,pane,datapath=None,**kwargs):
        bc = pane.borderContainer()
        fb = bc.contentPane(region='top').formbuilder(datapath=datapath)
        fb.dbSelect(value='^.parent_service_id',lbl='Parent service',hasDownArrow=True,
                    selected_service_name='.parent_service',
                    dbtable='sys.service',
                    condition="""$service_type=:stype AND $implementation!='symbolic' AND
                    $service_name!=:me""",
                    condition_stype='storage', condition_me='^.service_name')
        
        fb.textbox(value='^.relative_path',lbl='Relative path')
        bc.storageTreeFrame(frameCode='relativeStorage',storagepath='=#FORM.record.service_name?=#v+":"',
                                border='1px solid silver',margin='2px',rounded=4,
                                region='center',preview_region='right',
                                store__onBuilt=True,
                                preview_border_left='1px solid silver',preview_width='50%')


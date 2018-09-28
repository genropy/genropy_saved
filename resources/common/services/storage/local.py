#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-


from gnr.lib.services.storage import StorageService
from gnr.web.gnrbaseclasses import BaseComponent
import os
import shutil

class Service(StorageService):
    def __init__(self, parent=None, name=None, base_path=None,**kwargs):
        self.parent = parent
        self.name = name
        self.base_path = base_path

    @property
    def location_identifier(self):
        return 'localfs'

    def internal_path(self, path):
        return os.path.join(self.base_path, *(path.split('/')))

    def delete(self, path):
        return os.unlink(self.internal_path(path))

    def open(self, path, mode='rb'):
        return open(self.internal_path(path), mode=mode)

    def renameNode(self, sourceNode=None, destNode=None):
        shutil.move(sourceNode.internal_path, destNode.internal_path)

    def duplicateNode(self, sourceNode=None, destNode=None):
        shutil.copy2(sourceNode.internal_path, destNode.internal_path)

    
    def url(self, path):
        url = '%s/_storage/%s/%s' %(self.parent.external_host, self.name, path)
        return url

class ServiceParameters(BaseComponent):

    def service_parameters(self,pane,datapath=None,**kwargs):
        fb = pane.formbuilder(datapath=datapath)
        fb.textbox(value='^.base_path',lbl='Base path')
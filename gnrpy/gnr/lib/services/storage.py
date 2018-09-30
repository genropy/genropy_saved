#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-

import os
import re

from datetime import datetime
from gnr.core import gnrstring
from gnr.core.gnrbag import Bag,DirectoryResolver,BagResolver
from gnr.lib.services import GnrBaseService

class NotExistingStorageNode(Exception):
    pass

class StorageNode(object):

    def __init__(self, parent=None, path=None, service=None, autocreate=None,
        must_exist=False):
        self.parent = parent
        self.path = path
        self.service = service
        if must_exist and not self.service.exists(self.path):
            raise NotExistingStorageNode

    @property
    def ext(self):
        return self.service.extension(self.path)

    @property
    def is_dir(self):
        return self.path.endswith('/')

    @property
    def internal_path(self):
        return self.service.internal_path(self.path)

    @property
    def exists(self):
        return self.service.exists(self.path)

    def open(self, mode='rb'):
        return self.service.open(self.path, mode=mode)

    @property
    def url(self):
        return self.service.url(self.path)

    def delete(self):
        return self.service.delete(self.path)

    def move(self, dest=None):
        self.service.move(source=self.path, dest=dest)
        self.path = dest.path
        self.service = dest.service

    def copy(self, dest=None):
        return self.service.copy(source=self.path, dest=dest)

    def serve(self, environ, start_response):
        return self.service.serve(self.path, environ, start_response)

class StorageService(GnrBaseService):

    def _getNode(self, node=None):
        return node if isinstance(node, StorageNode) else self.parent.storage(node)

    def internal_path(self, path=None):
        pass

    def base_name(self, path=None):
        return path.split('/')[-1]

    def extension(self, path=None):
        base_name = self.base_name(path)
        return os.path.splitext(base_name)[-1]


    @property
    def location_identifier(self):
        pass

    def open(self,*args,**kwargs):
        pass

    def url(self,*args, **kwargs):
        pass

    def symbolic_url(self,*args, **kwargs):
        pass

    def delete(self,*args, **kwargs):
        pass

    def copyNodeContent(self, sourceNode=None, destNode=None):
        with sourceNode.open(mode='rb') as sourceFile:
            with destNode.open(mode='wb') as destFile:
                destFile.write(sourceFile.read())

    def copy(self, source=None, dest=None):
        sourceNode = self._getNode(source)
        destNode = self._getNode(dest)
        if destNode.service.location_identifier == sourceNode.service.location_identifier:
            sourceNode.service.duplicateNode(source=sourceNode, 
                dest = destNode)
        else:
            self.copyNodeContent(sourceNode=sourceNode, destNode=destNode)
        return destNode

    def move(self, source=None, dest=None):
        sourceNode = self._getNode(source)
        destNode = self._getNode(dest)
        if destNode.service == sourceNode.service:
            sourceNode.service.renameNode(sourceNode=sourceNode, 
                destNode=destNode)
        else:
            self.copyNodeContent(sourceNode=sourceNode, destNode=destNode)
        sourceNode.delete()
        return destNode

    def serve(self, path):
        pass
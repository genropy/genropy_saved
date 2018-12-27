#!/usr/bin/env pythonw
# -*- coding: utf-8 -*-

from gnr.lib.services.storage import BaseLocalService
from gnr.web.gnrbaseclasses import BaseComponent
import os
import tempfile
from gnr.core.gnrsys import expandpath

class Service(BaseLocalService):

    def __init__(self, parent=None, base_path=None,**kwargs):
        super(Service,self).__init__(parent=parent, base_path='/', **kwargs)
    
    def expandpath(self,path):
        return expandpath(path)

    def serve(self, path, environ, start_response, download=False, download_name=None, **kwargs):
        return self.parent.not_found_exception(environ, start_response)

    def url(self, *args, **kwargs):
        return ''


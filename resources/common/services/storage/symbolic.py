#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-


from gnr.lib.services.storage import StorageService
from gnr.web.gnrbaseclasses import BaseComponent
import os
import shutil
from paste import fileapp
from paste.httpheaders import ETAG

class Service(Local):

    @property
    def location_identifier(self):
        return 'symbolic '

    def internal_path(self, path):
        path_list = path.split('/')
        base_path = self.site.resources.get(path_list[0])
        if base_path:
            return os.path.join(base_path, *(path[1:]))

    def url(self, path):
        url = '%s/_rsrc/%s/%s' %(self.parent.external_host, path)
        return url

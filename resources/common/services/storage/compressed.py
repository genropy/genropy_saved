#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-


from gnr.lib.services.storage import StorageService
from gnr.web.gnrbaseclasses import BaseComponent
import os
import shutil
from paste import fileapp
from paste.httpheaders import ETAG
from smart_open import smart_open
class Service(StorageService):
    def __init__(self, parent=None, base_path=None, **kwargs):
        self.parent = parent
        self.base_path = base_path
        self.compression_mode = 'gz'

    @property
    def location_identifier(self):
        return 'compressedfs'

    def internal_path(self, path):
        return "%s.%s"%(os.path.join(self.base_path, *(path.split('/'))),self.compression_mode)

    def delete(self, path):
        return os.unlink(self.internal_path(path))

    def open(self, path, mode='rb'):
        print self.internal_path(path)
        return smart_open(self.internal_path(path), mode=mode)

    def renameNode(self, sourceNode=None, destNode=None):
        shutil.move(sourceNode.internal_path, destNode.internal_path)

    def duplicateNode(self, sourceNode=None, destNode=None):
        shutil.copy2(sourceNode.internal_path, destNode.internal_path)

    def url(self, path):
        url = '%s/_storage/%s/%s' %(self.parent.external_host, self.service_name, path)
        return url

    def serve(self, path, environ, start_response, download=False, download_name=None, **kwargs):
        fullpath = self.internal_path(path)
        if not fullpath:
            return self.parent.not_found_exception(environ, start_response)
        existing_doc = os.path.exists(fullpath)
        if not existing_doc and '_lazydoc' in kwargs:
            existing_doc = self.build_lazydoc(kwargs['_lazydoc'],fullpath=fullpath)
        if not existing_doc:
            if kwargs.get('_lazydoc'):
                headers = []
                start_response('200 OK', headers)
                return ['']
            return self.parent.not_found_exception(environ, start_response)
        if_none_match = environ.get('HTTP_IF_NONE_MATCH')
        if if_none_match:
            if_none_match = if_none_match.replace('"','')
            stats = os.stat(fullpath)
            mytime = stats.st_mtime
            size = stats.st_size
            my_none_match = "%s-%s"%(str(mytime),str(size))
            if my_none_match == if_none_match:
                headers = []
                ETAG.update(headers, my_none_match)
                start_response('304 Not Modified', headers)
                return [''] # empty body
        file_args = dict()
        if download or download_name:
            download_name = download_name or os.path.basename(fullpath)
            file_args['content_disposition'] = "attachment; filename=%s" % download_name
        file_args['content_encoding'] = 'gzip'
        file_responder = fileapp.FileApp(fullpath, **file_args)
        if self.parent.cache_max_age:
            file_responder.cache_control(max_age=self.parent.cache_max_age)
        return file_responder(environ, start_response)

class ServiceParameters(BaseComponent):

    def service_parameters(self,pane,datapath=None,**kwargs):
        fb = pane.formbuilder(datapath=datapath)
        fb.textbox(value='^.base_path',lbl='Base path')
        fb.filteringselect(value='^.compression_mode', values='gz:Gzip,bz2:Bzip2',lbl='Compression mode')
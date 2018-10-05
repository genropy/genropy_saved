#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-

import os
import re

from datetime import datetime
from gnr.core import gnrstring
from gnr.core.gnrbag import Bag,DirectoryResolver,BagResolver
from gnr.lib.services import GnrBaseService,BaseServiceType
import os
import shutil
from paste import fileapp
from paste.httpheaders import ETAG

class NotExistingStorageNode(Exception):
    pass

class ServiceType(BaseServiceType):
    def conf_site(self):
        return dict(implementation='local',base_path=self.site.site_static_dir)

    def conf_rsrc(self):
        return dict(implementation='symbolic')

    def conf_pkg(self):
        return dict(implementation='symbolic')

    def conf_dojo(self):
        return dict(implementation='symbolic')

    def conf_conn(self):
        return dict(implementation='symbolic')

    def conf_page(self):
        return dict(implementation='symbolic')

    def conf_temp(self):
        return dict(implementation='symbolic')

    def conf_gnr(self):
        return dict(implementation='symbolic')

    def conf_pages(self):
        return dict(implementation='symbolic')

    def conf_user(self):
        return dict(implementation='symbolic')

class StorageNode(object):

    def __init__(self, parent=None, path=None, service=None, autocreate=None,
        must_exist=False):
        self.parent = parent
        self.path = path
        self.service = service
        if must_exist and not self.service.exists(self.path):
            raise NotExistingStorageNode
    @property
    def fullpath(self):
        return "%s:%s"%(self.service.service_name, self.path)

    @property
    def ext(self):
        return self.service.extension(self.path)

    @property
    def isdir(self):
        return self.service.isdir(self.path)

    def listdir(self):
        if self.isdir:
            return self.service.listdir(self.path)

    @property
    def internal_path(self, **kwargs):
        return self.service.internal_path(self.path)

    @property
    def base_name(self, **kwargs):
        return self.service.base_name(self.path)

    @property
    def exists(self):
        return self.service.exists(self.path)

    def open(self, mode='rb'):
        return self.service.open(self.path, mode=mode)

    def url(self, **kwargs):
        return self.service.url(self.path, **kwargs)

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


class BaseLocalService(StorageService):
    def __init__(self, parent=None, base_path=None,**kwargs):
        self.parent = parent
        self.base_path = base_path

    @property
    def location_identifier(self):
        return 'localfs'

    def internal_path(self, path, **kwargs):
        return os.path.join(self.base_path, *(path.split('/')))

    def delete(self, path):
        return os.unlink(self.internal_path(path))

    def open(self, path, mode='rb'):
        return open(self.internal_path(path), mode=mode)

    def exists(self, path):
        return os.path.exists(self.internal_path(path))

    def isdir(self, path):
        return os.path.isdir(self.internal_path(path))

    def renameNode(self, sourceNode=None, destNode=None):
        shutil.move(sourceNode.internal_path(), destNode.internal_path())

    def duplicateNode(self, sourceNode=None, destNode=None):
        shutil.copy2(sourceNode.internal_path(), destNode.internal_path())

    def url(self, path, **kwargs):
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
        file_responder = fileapp.FileApp(fullpath, **file_args)
        if self.parent.cache_max_age:
            file_responder.cache_control(max_age=self.parent.cache_max_age)
        return file_responder(environ, start_response)

    def listdir(self, path, **kwargs):
        directory = os.listdir(self.internal_path(path))
        out = []
        for d in directory:
            subpath = os.path.join(path,d)
            out.append(StorageNode(parent=self.parent, path=subpath, service=self))
        return out

class StorageResolver(BagResolver):
    """TODO"""


    classKwargs = {'cacheTime': 500,
                   'readOnly': True,
                   'invisible': False,
                   'relocate': '',
                   'ext': 'xml',
                   'include': '',
                   'exclude': '',
                   'callback': None,
                   'dropext': False,
                   'processors': None
    }
    classArgs = ['storage','relocate']

    @property
    def site(self):
        return self._page.site

    def load(self):
        """TODO"""
        extensions = dict([((ext.split(':') + (ext.split(':'))))[0:2] for ext in self.ext.split(',')]) if self.ext else dict()
        extensions['directory'] = 'directory'
        result = Bag()
        try:
            if isinstance(self.storage, basestring):
                self.storage = self.site.storage(self.storage)
            directory = sorted(self.storage.listdir())
        except OSError:
            directory = []
        if not self.invisible:
            directory = [x for x in directory if not x.base_name.startswith('.')]
        for storagenode in directory:
            fname = storagenode.base_name
            nodecaption = fname
            fullpath = storagenode.fullpath
            addIt = True
            if storagenode.isdir:
                ext = 'directory'
                if self.exclude:
                    addIt = gnrstring.filter(fname, exclude=self.exclude, wildcard='*')
            else:
                if self.include or self.exclude:
                    addIt = gnrstring.filter(fname, include=self.include, exclude=self.exclude, wildcard='*')
                fname, ext = os.path.splitext(fname)
                ext = ext[1:]
            if addIt:
                label = self.makeLabel(fname, ext)
                processors = self.processors or {}
                processname = extensions.get(ext.lower(), None)
                handler = processors.get(processname)
                if handler is not False:
                    handler = handler or getattr(self, 'processor_%s' % extensions.get(ext.lower(), 'None'), None)
                handler = handler or self.processor_default
                try:
                    mtime = storagenode.mtime
                    atime = storagenode.atime
                    ctime = storagenode.size
                except:
                    mtime = None
                    ctime = None
                    atime = None
                    size = None
                caption = fname.replace('_',' ').strip()
                m=re.match(r'(\d+) (.*)',caption)
                caption = '!!%s %s' % (str(int(m.group(1))),m.group(2).capitalize()) if m else caption.capitalize()
                nodeattr = dict(file_name=fname, file_ext=ext, storage=storagenode.service.service_name,
                               abs_path=fullpath, mtime=mtime, atime=atime, ctime=ctime, nodecaption=nodecaption,
                               caption=caption,size=size)
                if self.callback:
                    cbres = self.callback(nodeattr=nodeattr)
                    if cbres is False:
                        continue
                result.setItem(label, handler(storagenode) ,**nodeattr)
        return result

    def makeLabel(self, name, ext):
        """TODO

        :param name: TODO
        :param ext: TODO"""
        if ext != 'directory' and not self.dropext:
            name = '%s_%s' % (name, ext)
        return name.replace('.', '_')

    def processor_directory(self, storagenode):
        """TODO

        :param path: TODO"""
        return StorageResolver(storagenode.fullpath, "%s/%s"%(self.relocate, storagenode.base_name), **self.instanceKwargs)

    def processor_xml(self, storagenode):
        """TODO

        :param path: TODO"""
        kwargs = dict(self.instanceKwargs)
        kwargs['storagenode'] = storagenode
        return XmlStorageResolver(**kwargs)

    processor_xsd = processor_xml

    processor_html = processor_xml


    def processor_txt(self, storagenode):
        """TODO

        :param path: TODO"""
        kwargs = dict(self.instanceKwargs)
        kwargs['storagenode'] = storagenode
        return TxtStorageResolver(**kwargs)

    def processor_default(self, path):
        """TODO

        :param path: TODO"""
        return None


class TxtStorageResolver(BagResolver):
    classKwargs = {'cacheTime': 500,
                   'readOnly': True
    }
    classArgs = ['storagenode']

    def load(self):
        with self.storagenode.open() as f:
            return f.read()

class XmlStorageResolver(BagResolver):
    classKwargs = {'cacheTime': 500,
                   'readOnly': True
    }
    classArgs = ['storagenode']

    def load(self):
        with self.storagenode.open() as xmlfile:
            b = Bag()
            b.fromXml(xmlfile.read())
            return b

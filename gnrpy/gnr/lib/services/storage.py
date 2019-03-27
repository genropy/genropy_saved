#!/usr/bin/env pythonw
# -*- coding: utf-8 -*-

import os
import re
import random
from datetime import datetime
from gnr.core import gnrstring
from gnr.core.gnrbag import Bag,DirectoryResolver,BagResolver
from gnr.lib.services import GnrBaseService,BaseServiceType
import os
import shutil
from gnr.core.gnrsys import expandpath
import mimetypes
from paste import fileapp
from paste.httpheaders import ETAG
from subprocess import call,check_call, check_output
class NotExistingStorageNode(Exception):
    pass

import sys
from collections import deque


class ExitStack(object):
    """Context manager for dynamic management of a stack of exit callbacks

    For example:

        with ExitStack() as stack:
            files = [stack.enter_context(open(fname)) for fname in filenames]
            # All opened files will automatically be closed at the end of
            # the with statement, even if attempts to open files later
            # in the list raise an exception

    """
    def __init__(self):
        self._exit_callbacks = deque()

    def pop_all(self):
        """Preserve the context stack by transferring it to a new instance"""
        new_stack = type(self)()
        new_stack._exit_callbacks = self._exit_callbacks
        self._exit_callbacks = deque()
        return new_stack

    def _push_cm_exit(self, cm, cm_exit):
        """Helper to correctly register callbacks to __exit__ methods"""
        def _exit_wrapper(*exc_details):
            return cm_exit(cm, *exc_details)
        _exit_wrapper.__self__ = cm
        self.push(_exit_wrapper)

    def push(self, exit):
        """Registers a callback with the standard __exit__ method signature

        Can suppress exceptions the same way __exit__ methods can.

        Also accepts any object with an __exit__ method (registering a call
        to the method instead of the object itself)
        """
        # We use an unbound method rather than a bound method to follow
        # the standard lookup behaviour for special methods
        _cb_type = type(exit)
        try:
            exit_method = _cb_type.__exit__
        except AttributeError:
            # Not a context manager, so assume its a callable
            self._exit_callbacks.append(exit)
        else:
            self._push_cm_exit(exit, exit_method)
        return exit # Allow use as a decorator

    def callback(self, callback, *args, **kwds):
        """Registers an arbitrary callback and arguments.

        Cannot suppress exceptions.
        """
        def _exit_wrapper(exc_type, exc, tb):
            callback(*args, **kwds)
        # We changed the signature, so using @wraps is not appropriate, but
        # setting __wrapped__ may still help with introspection
        _exit_wrapper.__wrapped__ = callback
        self.push(_exit_wrapper)
        return callback # Allow use as a decorator

    def enter_context(self, cm):
        """Enters the supplied context manager

        If successful, also pushes its __exit__ method as a callback and
        returns the result of the __enter__ method.
        """
        # We look up the special methods on the type to match the with statement
        _cm_type = type(cm)
        _exit = _cm_type.__exit__
        result = _cm_type.__enter__(cm)
        self._push_cm_exit(cm, _exit)
        return result

    def close(self):
        """Immediately unwind the context stack"""
        self.__exit__(None, None, None)

    def __enter__(self):
        return self

    def __exit__(self, *exc_details):
        # We manipulate the exception state so it behaves as though
        # we were actually nesting multiple with statements
        frame_exc = sys.exc_info()[1]
        def _fix_exception_context(new_exc, old_exc):
            while 1:
                exc_context = new_exc.__context__
                if exc_context in (None, frame_exc):
                    break
                new_exc = exc_context
            new_exc.__context__ = old_exc

        # Callbacks are invoked in LIFO order to match the behaviour of
        # nested context managers
        suppressed_exc = False
        while self._exit_callbacks:
            cb = self._exit_callbacks.pop()
            try:
                if cb(*exc_details):
                    suppressed_exc = True
                    exc_details = (None, None, None)
            except:
                new_exc_details = sys.exc_info()
                # simulate the stack of exceptions by setting the context
                _fix_exception_context(new_exc_details[1], exc_details[1])
                if not self._exit_callbacks:
                    raise
                exc_details = new_exc_details
        return suppressed_exc
class LocalPath(object):
    def __init__(self, fullpath=None):
        self.fullpath = fullpath

    def __enter__(self):
        return self.fullpath

    def __exit__(self, exc, value, tb):
        pass

class ServiceType(BaseServiceType):
    
    def conf_home(self):
        return dict(implementation='local',base_path=self.site.site_static_dir)

    def conf_mail(self):
        return dict(implementation='local',base_path='%s/mail' %self.site.site_static_dir)

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
    
    def conf__raw_(self):
        return dict(implementation='raw')

    #def conf_vol(self):
    #    return dict(implementation='symbolic')
    def getServiceFactory(self,implementation=None):
        return self.implementations.get(implementation)
    
class StorageNode(object):

    @classmethod
    def fromPath(cls, path, parent=None):
        if isinstance(path, cls):
            return path
        if not ':' in path:
            path = '_raw_:%s'%path
        return parent.storageNode(path)

    def __init__(self, parent=None, path=None, service=None, autocreate=None,must_exist=False, mode='r'):
        self.service = service
        self.parent = parent
        self.path = self.service.expandpath(path)
        if must_exist and not self.service.exists(self.path):
            raise NotExistingStorageNode
        self.mode = mode
        self.autocreate = autocreate

    @property
    def md5hash(self):
        return self.service.md5hash(self.path)

    @property
    def fullpath(self):
        return self.service.fullpath(self.path)

    @property
    def ext(self):
        return self.service.extension(self.path)

    @property
    def isdir(self):
        return self.service.isdir(self.path)

    def children(self):
        if self.isdir:
            return self.service.children(self.path)

    def listdir(self):
        if self.isdir:
            return self.service.listdir(self.path)
    
    def mkdir(self, *args):
        return self.service.mkdir(self.path, *args)

    @property
    def internal_path(self, **kwargs):
        return self.service.internal_path(self.path)

    @property
    def basename(self, **kwargs):
        return self.service.basename(self.path)

    @property
    def cleanbasename(self, **kwargs):
        return os.path.splitext(self.service.basename(self.path))[0]

    @property
    def isfile(self):
        return self.service.isfile(self.path) 

    @property
    def exists(self):
        return self.service.exists(self.path)
    
    @property
    def mtime(self):
        return self.service.mtime(self.path)

    @property
    def size(self):
        return self.service.size(self.path)
    
    @property
    def dirname(self):
        return '%s:%s'%(self.service.service_name,os.path.dirname(self.path))
        
    @property
    def parentStorageNode(self):
        return self.parent.storageNode(self.dirname)
    
    def splitext(self):
        return os.path.splitext(self.path)

    def base64(self, mime=None):
        return self.service.base64(self.path, mime=mime)

    def open(self, mode='rb'):
        self.service.autocreate(self.path, autocreate=-1)
        return self.service.open(self.path, mode=mode)

    def url(self, **kwargs):
        return self.service.url(self.path, **kwargs)

    def internal_url(self, **kwargs):
        return self.service.internal_url(self.path, **kwargs)

    def delete(self):
        return self.service.delete(self.path)

    def move(self, dest=None):
        dest = self.service.move(source=self, dest=dest)
        self.path = dest.path
        self.service = dest.service

    def copy(self, dest=None):
        return self.service.copy(source=self, dest=dest)

    def serve(self, environ, start_response, **kwargs):
        return self.service.serve(self.path, environ, start_response, **kwargs)

    def local_path(self, mode=None, keep=False):
        self.service.autocreate(self.path, autocreate=-1)
        return self.service.local_path(self.path, mode=mode or self.mode, keep=keep)

    def child(self, path=None):
        if self.path and self.path[-1]!='/':
            path = '/%s'%path
        return self.service.parent.storageNode('%s%s'%(self.fullpath,path))

    @property
    def mimetype(self):
        return self.service.mimetype(self.path)

class StorageService(GnrBaseService):

    def _getNode(self, node=None):
        return node if isinstance(node, StorageNode) else self.parent.storageNode(node)

    def internal_path(self, *args, **kwargs):
        pass

    def md5hash(self,*args):
        pass

    def fullpath(self, path):
        return "%s:%s"%(self.service_name, path)

    def local_path(self, *args, **kwargs):
        pass
    
    def expandpath(self,path):
        return path

    def basename(self, path=None):
        return self.split_path(path)[-1]
    
    def extension(self, path=None):
        basename = self.basename(path)
        return os.path.splitext(basename)[-1].strip('.')

    def split_path(self, path):
        return path.replace('/','\t').replace(os.path.sep,'/').replace('\t','/').split('/')

    def sync_to_service(self, dest_service, subpath='', skip_existing=True, skip_same_size=False,
        thermo=None, done_list=None, doneCb=None):
        assert not (skip_existing and skip_same_size), 'use either skip_existing or skip_same_size'
        done_list = done_list or []
        storage_resolver = StorageResolver(self.parent.storageNode('%s:%s'%(self.service_name,subpath)))
        to_copy = []
        def checkSync(node):
            if node.attr.get('file_ext') == 'directory':
                return
            fullpath = node.attr.get('abs_path')
            if fullpath in done_list:
                return
            src_node = self.parent.storageNode(fullpath)
            rel_path = fullpath.replace('%s:'%self.service_name,'',1)
            dest_node = self.parent.storageNode('%s:%s'%(dest_service,rel_path))
            if skip_existing or skip_same_size:
                if dest_node.exists:
                    size = dest_node.size if skip_same_size else node.attr.get('size')
                    if size == node.attr.get('size')==dest_node.size:
                        return

            to_copy.append((src_node, dest_node))
        storage_resolver().walk(checkSync, _mode='')
        to_copy = thermo(to_copy) if thermo else to_copy
        for srcNode, destNode in to_copy:
            self.copy(srcNode, destNode)
            if doneCb:
                doneCb(srcNode)

    def mimetype(self, *args,**kwargs):
        return mimetypes.guess_type(self.internal_path(*args))[0] or 'application/octet-stream'

    def base64(self, *args, **kwargs):
        """Convert a file (specified by a path) into a data URI."""
        import base64
        if not self.exists(*args):
            return u''
        mime = kwargs.get('mime', False)
        if mime is True:
            mime = self.mimetype(*args)
        with self.open(*args, mode='rb') as fp:
            data = fp.read()
            data64 = ''.join(base64.encodestring(data).splitlines())
            if mime:
                result  ='data:%s;base64,%s' % (mime, data64)
            else:
                result = '%s' % data64
            return result

    def internal_url(self, *args, **kwargs):
        outlist = [self.parent.external_host, '_storage', self.service_name]
        outlist.extend(args)
        url = '/'.join(outlist)
        if not kwargs:
            return url
        nocache = kwargs.pop('nocache', None)
        if nocache:
            if self.exists(*args):
                mtime = self.mtime(*args)
            else:
                mtime = random.random() * 100000
            kwargs['mtime'] = '%0.0f' % (mtime)

        url = '%s?%s' % (url, '&'.join(['%s=%s' % (k, v) for k, v in kwargs.items()]))
        return url

    @property
    def location_identifier(self):
        pass

    def open(self,*args,**kwargs):
        pass

    def url(self,*args, **kwargs):
        pass

    def symbolic_url(self,*args, **kwargs):
        pass

    def mtime(self, path):
        pass

    def size(self, path):
        pass

    def delete(self, *args):
        if self.isdir(*args):
            self.delete_dir(*args)
        else:
            self.delete_file(*args)


    def autocreate(self, *args, **kwargs):

        autocreate=kwargs.pop('autocreate', None)
        if not autocreate:
            return
        args = self.split_path('/'.join(args))
        if autocreate != True:
            autocreate_args = args[:autocreate]
        else:
            autocreate_args = args
        
        dest_dir = StorageNode(parent=self.parent,
            service=self,path='/'.join(autocreate_args))
        if not dest_dir.exists:
            self.makedirs(dest_dir.path)

    def copyNodeContent(self, sourceNode=None, destNode=None):
        with sourceNode.open(mode='rb') as sourceFile:
            with destNode.open(mode='wb') as destFile:
                destFile.write(sourceFile.read())

    def copy(self, source=None, dest=None):
        sourceNode = self._getNode(source)
        destNode = self._getNode(dest)
        if destNode.service.location_identifier == sourceNode.service.location_identifier:
            sourceNode.service.duplicateNode(sourceNode=sourceNode,
                destNode = destNode)
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

    def serve(self, path, **kwargs):
        pass

    def _call(self, call_args=None, call_kwargs=None, cb=None, cb_args=None, cb_kwargs=None, return_output=False):
        args_list = []
        with ExitStack() as stack:
            for arg in call_args:
                if isinstance(arg, StorageNode):
                    arg = stack.enter_context(arg.local_path())
                args_list.append(arg)
            call_fn = check_output if return_output else check_call
            result = call_fn(args_list, **call_kwargs)
            if cb:
                cb(*cb_args, **cb_kwargs)
            return result

    def call(self, args, **kwargs):
        cb = kwargs.pop('cb', None)
        cb_args = kwargs.pop('cb', None)
        cb_kwargs = kwargs.pop('cb', None)
        run_async = kwargs.pop('run_async', None)
        return_output = kwargs.pop('return_output', None)
        call_params = dict(call_args=args,call_kwargs=kwargs, cb=cb, cb_args=cb_args, cb_kwargs=cb_kwargs, return_output=return_output)
        if run_async:
            import thread
            thread.start_new_thread(self._call,(),call_params)
        else:
            return self._call(**call_params)

    def listdir(self, *args, **kwargs):
        return [sn.fullpath for sn in self.children(*args, **kwargs)]

class BaseLocalService(StorageService):
    def __init__(self, parent=None, base_path=None,**kwargs):
        self.parent = parent
        self.base_path =  expandpath(base_path) if base_path else None

    @property
    def location_identifier(self):
        return 'localfs'

    def internal_path(self, *args, **kwargs):
        out_list = [self.base_path]
        out_list.extend(args)
        outpath = os.path.join(*out_list)
        return outpath

    def delete_dir(self, *args):
        shutil.rmtree(self.internal_path(*args))

    def delete_file(self, *args):
        return os.unlink(self.internal_path(*args))

    def open(self, *args, **kwargs):
        return open(self.internal_path(*args), **kwargs)

    def exists(self, *args):
        return os.path.exists(self.internal_path(*args))

    def mtime(self, *args):
        stats = os.stat(self.internal_path(*args))
        return stats.st_mtime

    def size(self, *args):
        stats = os.stat(self.internal_path(*args))
        return stats.st_mtime

    def local_path(self, *args, **kwargs): #TODO: vedere se fare così o con altro metodo
        mode = kwargs.get('mode', 'r')
        internalpath = self.internal_path(*args)
        return LocalPath(fullpath=internalpath)

    def makedirs(self, *args, **kwargs):
        os.makedirs(self.internal_path(*args))

    def mkdir(self, *args, **kwargs):
        if not self.exists(*args):
            os.mkdir(self.internal_path(*args))

    def isdir(self, *args):
        if self.base_path is None:
            return False
        return os.path.isdir(self.internal_path(*args))

    def isfile(self, *args):
        return os.path.isfile(self.internal_path(*args))
    
    def md5hash(self,*args):
        import hashlib
        BLOCKSIZE = 65536
        hasher = hashlib.md5()
        with self.open(*args, mode='rb') as afile:
            buf = afile.read(BLOCKSIZE)
            while len(buf) > 0:
                hasher.update(buf)
                buf = afile.read(BLOCKSIZE)
        return hasher.hexdigest()

    def renameNode(self, sourceNode=None, destNode=None):
        destNode.service.autocreate(destNode.path, autocreate=-1)
        shutil.move(sourceNode.internal_path, destNode.internal_path)

    def duplicateNode(self, sourceNode=None, destNode=None):
        destNode.service.autocreate(destNode.path, autocreate=-1)
        shutil.copy2(sourceNode.internal_path, destNode.internal_path)

    def url(self, *args, **kwargs):
        return self.internal_url(*args, **kwargs)

    def serve(self, path, environ, start_response, download=False, download_name=None, **kwargs):
        fullpath = self.internal_path(path)
        if not fullpath:
            return self.parent.not_found_exception(environ, start_response)
        existing_doc = os.path.exists(fullpath)
        if not existing_doc:
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


    def children(self, *args, **kwargs):
        directory = os.listdir(self.internal_path(*args))
        out = []
        for d in directory:
            subpath = os.path.join(os.path.join(*args),d)
            out.append(StorageNode(parent=self.parent, path=subpath, service=self))
        return out

class StorageResolver(BagResolver):
    """TODO"""


    classKwargs = {'cacheTime': 500,
                   'readOnly': True,
                   'invisible': False,
                   'relocate': '',
                   'ext': None,
                   'include': '',
                   'exclude': '',
                   'callback': None,
                   'dropext': False,
                   'processors': None,
                   '_page':None
    }
    classArgs = ['storageNode','relocate']

    def resolverSerialize(self):
        attr = super(StorageResolver, self).resolverSerialize()
        attr['kwargs'].pop('_page',None)
        return attr

    @property
    def service(self):
        return self.storageNode.service

    def load(self):
        """TODO"""
        extensions = dict([((ext.split(':') + (ext.split(':'))))[0:2] for ext in self.ext.split(',')]) if self.ext else dict()
        extensions['directory'] = 'directory'
        result = Bag()
        self.storageNode = self._page.site.storageNode(self.storageNode)
        try:
            directory = sorted(self.storageNode.children() or [])
        except OSError:
            directory = []
        if not self.invisible:
            directory = [x for x in directory if not x.basename.startswith('.')]
        for storagenode in directory:
            fname = storagenode.basename
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
                    size = storagenode.size
                except:
                    mtime = None
                    size = None
                caption = fname.replace('_',' ').strip()
                m=re.match(r'(\d+) (.*)',caption)
                caption = '!!%s %s' % (str(int(m.group(1))),m.group(2).capitalize()) if m else caption.capitalize()
                nodeattr = dict(file_name=fname, file_ext=ext, storage=storagenode.service.service_name,
                               abs_path=fullpath,url=storagenode.url(), mtime=mtime, nodecaption=nodecaption,
                               caption=caption,size=size, 
                               internal_url=storagenode.internal_url())
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
        return StorageResolver(storagenode.fullpath, **self.instanceKwargs)

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

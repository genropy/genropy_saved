
# -*- coding: UTF-8 -*-
from gnr.core.gnrbag import Bag
from gnr.core import gnrstring
import inspect
import os
import sys
from gnr.core.gnrsys import expandpath
from paste import fileapp
from paste.httpheaders import ETAG
import random
import tempfile

class StaticHandlerManager(object):
    """ This class handles the StaticHandlers"""

    def __init__(self, site):
        self.site = site
        self.statics = Bag()
        

    def addAllStatics(self, module=None):
        """inspect self (or other modules) for StaticHandler subclasses and 
        do addStatic for each"""
        module = module or sys.modules[self.__module__]

        def is_StaticHandler(cls):
            return inspect.isclass(cls) and issubclass(cls, StaticHandler) and cls is not StaticHandler

        statichandler_classes = inspect.getmembers(module, is_StaticHandler)
        for statichandler in statichandler_classes:
            self.add(statichandler[1])

    def add(self, static_handler_factory, **kwargs):
        static_handler = static_handler_factory(self.site, **kwargs)
        self.statics.setItem(static_handler.prefix, static_handler, **kwargs)

    def get(self, static_name):
        return self.statics[static_name]

    def fileserve(self, f, environ, start_response, download=False, **kwargs):
        return StaticHandler(self.site).serve(f, environ,start_response, download=download, **kwargs)

    def static_dispatcher(self, path_list, environ, start_response, download=False, **kwargs):
        handler = self.get(path_list[0][1:])
        if handler:
            result = handler.serve(path_list, environ, start_response, download=download, **kwargs)

            return result
        else:
            return self.site.not_found_exception(environ, start_response)


class StaticHandler(object):
    """ implementor=self.site.get_implementor('dojo')
    "/_dojo/11/dojo/dojo/dojo.js"=implementor.relative_url(*args)
    "http://www.pippone.com/mysite/_dojo/11/dojo/dojo/dojo.js"=implementor.external_url(*args)
    "http://localhost:8088/_dojo/11/dojo/dojo/dojo.js"=implementor.local_url(*args)
    result=implementor.serve(*args)
    '/Users/genro/develop/dojo11/dojo/dojo.js'=implementor.path(*args)
    implementor()
    def dojo_static_path(self, version,*args):
        return expandpath(os.path.join(self.dojo_path[version], *args))

    def dojo_static_url(self, version,*args):
        return '%s_dojo/%s/%s'%(self.home_uri,version,'/'.join(args))"""

    def __init__(self, site, **kwargs):
        self.site = site

    @property
    def home_uri(self):
        """TODO"""
        return self.site.default_uri

    def absolute_url(self, external=True, *args):
        pass

    def build_lazydoc(self,lazydoc,ext=None):
        ext = ext.replace('.','') if ext else None 
        table,pkey,method = gnrstring.splitAndStrip(lazydoc,sep=',',fixed=3)
        dflt_method = 'create_cached_document_%s' %ext if ext else 'create_cached_document'
        m = getattr(self.site.db.table(table),(method or dflt_method),None)
        if m:
            result = m(pkey)
            return result is not False

    def serve(self, f, environ, start_response, download=False, **kwargs):
        if isinstance(f,list):
            fullpath = self.path(*f[1:])
        elif isinstance(f,file):
            fullpath = f.name
        else:
            fullpath = f
        if not fullpath:
            return self.site.not_found_exception(environ, start_response)
        if not os.path.isabs(fullpath):
            fullpath = os.path.normpath(os.path.join(self.site_path, fullpath))
        existing_doc = os.path.exists(fullpath)
        if not existing_doc and '_lazydoc' in kwargs:
            existing_doc = self.build_lazydoc(kwargs['_lazydoc'],ext=os.path.splitext(fullpath)[-1])
        if not existing_doc:
            if kwargs.get('_lazydoc'):
                headers = []
                start_response('200 OK', headers)
                return ['']
            return self.site.not_found_exception(environ, start_response)
        if_none_match = environ.get('HTTP_IF_NONE_MATCH')
        if if_none_match:
            mytime = os.stat(fullpath).st_mtime
            if str(mytime) == if_none_match:
                headers = []
                ETAG.update(headers, mytime)
                start_response('304 Not Modified', headers)
                return [''] # empty body
        file_args = dict()
        if download:
            file_args['content_disposition'] = "attachment; filename=%s" % os.path.basename(fullpath)
        file_responder = fileapp.FileApp(fullpath, **file_args)
        if self.site.cache_max_age:
            file_responder.cache_control(max_age=self.site.cache_max_age)
        return file_responder(environ, start_response)

    def kwargs_url(self, *args, **kwargs):
        url = self.url(*args)
        fpath = self.path(*args)
        if not kwargs:
            return url
        nocache = kwargs.pop('nocache', None)
        if nocache:
            if os.path.exists(fpath):
                mtime = os.stat(fpath).st_mtime
            else:
                mtime = random.random() * 100000
            kwargs['mtime'] = '%0.0f' % (mtime)

        url = '%s?%s' % (url, '&'.join(['%s=%s' % (k, v) for k, v in kwargs.items()]))
        return url


class DojoStaticHandler(StaticHandler):
    prefix = 'dojo'

    def url(self, version, *args, **kwargs):
        return '%s_dojo/%s/%s' % (self.home_uri, version, '/'.join(args))

    def path(self, version, *args, **kwargs):
        return expandpath(os.path.join(self.site.dojo_path[version], *args))

class VolumesStaticHandler(StaticHandler):
    prefix = 'vol'

    def __init__(self, *args, **kwargs):
        super(VolumesStaticHandler, self).__init__(*args,**kwargs)
        self.volumes = dict()
        sitevolumes = self.site.config.getItem('volumes')
        if sitevolumes:
            self.volumes = dict([(n.label,n.attr['path']) for n in sitevolumes])

    def url(self, volume, *args, **kwargs):
        return '%s_vol/%s/%s' % (self.home_uri, volume, '/'.join(args))

    def path(self, volume, *args, **kwargs):
        vpath = self.volumes.get(volume,volume)
        return expandpath(os.path.join(self.site.site_static_dir,vpath, *args))

class SiteStaticHandler(StaticHandler):
    prefix = 'site'

    def url(self, *args, **kwargs):
        return '%s_site/%s' % (self.home_uri, '/'.join(args))

    def path(self, *args):
        return expandpath(os.path.join(self.site.site_static_dir, *args))

class PkgStaticHandler(StaticHandler):
    prefix = 'pkg'

    def path(self, pkg, *args,**kwargs):
        return os.path.join(self.site.gnrapp.packages[pkg].packageFolder, *args)

    def url(self, pkg, *args, **kwargs):
        return '%s_pkg/%s/%s' % (self.home_uri, pkg, '/'.join(args))

class RsrcStaticHandler(StaticHandler):
    prefix = 'rsrc'

    def path(self, resource_id, *args):
        resource_path = self.site.resources.get(resource_id)
        if resource_path:
            return os.path.join(resource_path, *args)

    def url(self, resource_id, *args, **kwargs):
        return '%s_rsrc/%s/%s' % (self.home_uri, resource_id, '/'.join(args))


class PagesStaticHandler(StaticHandler):
    prefix = 'pages'

    def path(self, *args):
        return os.path.join(self.site_path, 'pages', *args)

    def url(self, *args, **kwargs):
        return '%s_pages/%s' % (self.home_uri, '/'.join(args))


class GnrStaticHandler(StaticHandler):
    prefix = 'gnr'

    def path(self, version, *args):
        return expandpath(os.path.join(self.site.gnr_path[version], *args))

    def url(self, version, *args, **kwargs):
        return '%s_gnr/%s/%s' % (self.home_uri, version, '/'.join(args))

class ConnectionStaticHandler(StaticHandler):
    prefix = 'conn'

    def path(self, connection_id, *args):
        return os.path.join(self.site.site_path, 'data', '_connections', connection_id, *args)

    def url(self, connection_id, *args, **kwargs):
        return '%s_conn/%s/%s' % (self.home_uri, connection_id, '/'.join(args))

class PageStaticHandler(StaticHandler):
    prefix = 'page'

    def path(self, connection_id, page_id, *args):
        return os.path.join(self.site.site_path, 'data', '_connections', connection_id, page_id, *args)

    def url(self, connection_id, page_id, *args, **kwargs):
        return '%s_page/%s/%s/%s' % (self.home_uri, connection_id, page_id, '/'.join(args))


class TempStaticHandler(StaticHandler):
    prefix = 'temp'

    def path(self, *args):
        return os.path.join(tempfile.gettempdir(), *args)

    def url(self, connection_id, page_id, *args, **kwargs):
        pass
        #return '%s_page/%s/%s/%s' % (self.home_uri, connection_id, page_id, '/'.join(args))


class UserStaticHandler(StaticHandler):
    prefix = 'user'

    def path(self, user, *args):
        return os.path.join(self.site.site_path, 'data', '_users', user, *args)

    def url(self, user, *args):
        return '%s_user/%s/%s' % (self.home_uri, user, '/'.join(args))
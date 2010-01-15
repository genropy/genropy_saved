#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  untitled
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#
from gnr.web.gnrwebpage_proxy.gnrbaseproxy import GnrBaseProxy

class GnrWebUtils(GnrBaseProxy):
    
    def init(self, **kwargs):
        self.directory = self.page.site.site_path
        self.filename = self.page.filename
        self.canonical_filename = self.page.canonical_filename
    
    def siteFolder(self, *args,  **kwargs):
        """The http static root"""
        path = os.path.normpath(os.path.join(self.directory, '..', *args))
        relative=kwargs.get('relative')
        if relative:
            return self.diskPathToUri(path)
        return path
    
    def linkPage(self, *args, **kwargs):
        fromPage = kwargs.pop('fromPage')
        fromPageArgs = kwargs.pop('fromPageArgs')
        kwargs['relative'] = True
        topath = self.rootFolder(*args, **kwargs)
        if fromPage:
            fromPage = self.rootFolder(*args,**{'reverse':True})
            fromPage = '%s?%s' % (fromPage, urllib.urlencode(fromPageArgs))
            topath = '%s?%s' % (topath, urllib.urlencode({'fromPage':fromPage}))
        return topath

    def rootFolder(self, *args, **kwargs):
        """The mod_python root"""
        path = os.path.normpath(os.path.join(self.directory, *args))
    
        if kwargs.get('reverse'):
            return self.diskPathToUri(self.filename, fromfile=path)
        elif kwargs.get('relative'):
            return self.diskPathToUri(path)
        return path
    
    def pageFolder(self,*args,**kwargs):
        path = os.path.normpath(os.path.join(self.page.parentdirpath, *args))
        relative=kwargs.get('relative')
        if relative:
            return self.diskPathToUri(path)
        return path
    
    def relativePageFolder(self, *args, **kwargs):
        return os.path.dirname(self.canonical_filename).replace(self.page.siteFolder,'')

    def abspath(self, path):
        return os.path.normpath(os.path.join(os.path.dirname(self.filename), path))

    def absoluteDiskPath(self, path):
        os.path.join(self.page.siteFolder, path)
        return os.path.join(self.page.siteFolder, path)

    def diskPathToUri(self, tofile, fromfile=None):
        return self.page.diskPathToUri(tofile,fromfile=fromfile)
        fromfile = fromfile or self.filename
        basepath=os.path.normpath(os.path.join(self.directory, '..'))
        relUrl = tofile.replace(basepath,'').lstrip('/')
        path = fromfile.replace(basepath,'')
        rp = '../'*(len(path.split('/'))-2)
        return '%s%s' % (rp, relUrl)
    
    def readFile(self, path):
        if not path.startswith('/'):
            path=self.abspath(path)
        f=file(path,'r')
        result=f.read()
        f.close()
        return result
    
    def filename(self):
        return self.filename
 
    def dirbag(self, path='', base='', include='', exclude=None, ext=''):
        if base=='site':
            path = os.path.join(self.siteFolder, path)
        elif base=='root':
            path = os.path.join(self.rootFolder(), path)
        else:
            path = os.path.join(self.pageFolder(), path)
    
        result = Bag()
        path=os.path.normpath(path)
        path=path.rstrip('/')
        if not os.path.exists(path):
            os.makedirs(path)
        result[os.path.basename(path)] = DirectoryResolver(path, include=include, exclude=exclude, dropext=True, ext=ext)
        return result
    
    def pageTitle(self):
        return self.canonical_filename.replace(self.directory,'')
    
    def sendFile(self, content, filename=None, ext='', encoding='utf-8', mimetype='', sizelimit=200000):
        response = self.page.response
        if not mimetype:
            if ext=='xls':
                mimetype='application/vnd.ms-excel'
        filename = filename or self.page.request.uri.split('/')[-1]
        if encoding:
            content = content.encode(encoding)
        filename = filename.replace(' ','_').replace('/','-').replace(':','-').encode(encoding or 'ascii', 'ignore')
        if not sizelimit or len(content) < sizelimit:
            response.content_type = mimetype
            response.add_header("Content-Disposition", "attachment; filename=%s.%s" % (filename, ext))
        else:
            response.content_type = 'application/zip'
            response.add_header("Content-Disposition", "attachment; filename=%s.zip" % filename)
            zipresult = StringIO.StringIO()
            zip = zipfile.ZipFile(zipresult, mode='w', compression=zipfile.ZIP_DEFLATED)
            zipstring = zipfile.ZipInfo('%s.%s' % (filename, ext), datetime.datetime.now().timetuple()[:6])
            zipstring.compress_type = zipfile.ZIP_DEFLATED
            zip.writestr(zipstring, content)
            zip.close()
            content = zipresult.getvalue()
            zipresult.close()
        response.add_header("Content-Length", str(len(content)))
        response.write(content)

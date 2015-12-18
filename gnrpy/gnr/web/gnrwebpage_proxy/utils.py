#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  utils.py
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.

from gnr.web.gnrwebpage_proxy.gnrbaseproxy import GnrBaseProxy
import os
import urllib
import StringIO
import datetime
import zipfile
from gnr.core.gnrdecorator import public_method
from gnr.core.gnrbag import Bag, DirectoryResolver
from gnr.core.gnrlist import XlsReader,CsvReader
from gnr.core.gnrstring import slugify

class GnrWebUtils(GnrBaseProxy):


    def init(self, **kwargs):
        self.directory = self.page.site.site_path
        self.filename = self.page.filename
        self.canonical_filename = self.page.canonical_filename

    def siteFolder(self, *args, **kwargs):
        """The http static root"""
        path = os.path.normpath(os.path.join(self.directory, '..', *args))
        relative = kwargs.get('relative')
        if relative:
            return self.diskPathToUri(path)
        return path

    def linkPage(self, *args, **kwargs):
        fromPage = kwargs.pop('fromPage')
        fromPageArgs = kwargs.pop('fromPageArgs')
        kwargs['relative'] = True
        topath = self.rootFolder(*args, **kwargs)
        if fromPage:
            fromPage = self.rootFolder(*args, **{'reverse': True})
            fromPage = '%s?%s' % (fromPage, urllib.urlencode(fromPageArgs))
            topath = '%s?%s' % (topath, urllib.urlencode({'fromPage': fromPage}))
        return topath

    def rootFolder(self, *args, **kwargs):
        """The mod_python root"""
        path = os.path.normpath(os.path.join(self.directory, *args))

        if kwargs.get('reverse'):
            return self.diskPathToUri(self.filename, fromfile=path)
        elif kwargs.get('relative'):
            return self.diskPathToUri(path)
        return path

    def pageFolder(self, *args, **kwargs):
        path = os.path.normpath(os.path.join(self.page.parentdirpath, *args))
        relative = kwargs.get('relative')
        if relative:
            return self.diskPathToUri(path)
        return path

    def relativePageFolder(self, *args, **kwargs):
        return os.path.dirname(self.canonical_filename).replace(self.page.siteFolder, '')

    def abspath(self, path):
        return os.path.normpath(os.path.join(os.path.dirname(self.filename), path))

    def absoluteDiskPath(self, path):
        os.path.join(self.page.siteFolder, path)
        return os.path.join(self.page.siteFolder, path)

    def diskPathToUri(self, tofile, fromfile=None):
        return self.page.diskPathToUri(tofile, fromfile=fromfile)
        fromfile = fromfile or self.filename
        basepath = os.path.normpath(os.path.join(self.directory, '..'))
        relUrl = tofile.replace(basepath, '').lstrip('/')
        path = fromfile.replace(basepath, '')
        rp = '../' * (len(path.split('/')) - 2)
        return '%s%s' % (rp, relUrl)

    def readFile(self, path):
        if not path.startswith('/'):
            path = self.abspath(path)
        f = file(path, 'r')
        result = f.read()
        f.close()
        return result

    def filename(self):
        return self.filename

    def dirbag(self, path='', base='', include='', exclude=None, ext=''):
        if base == 'site':
            path = os.path.join(self.siteFolder, path)
        elif base == 'root':
            path = os.path.join(self.rootFolder(), path)
        else:
            path = os.path.join(self.pageFolder(), path)

        result = Bag()
        path = os.path.normpath(path)
        path = path.rstrip('/')
        if not os.path.exists(path):
            os.makedirs(path)
        result[os.path.basename(path)] = DirectoryResolver(path, include=include, exclude=exclude, dropext=True,
                                                           ext=ext)
        return result

    def pageTitle(self):
        return self.canonical_filename.replace(self.directory, '')

    def sendFile(self, content, filename=None, ext='', encoding='utf-8', mimetype='', sizelimit=200000):
        response = self.page.response
        if not mimetype:
            if ext == 'xls':
                mimetype = 'application/vnd.ms-excel'
        filename = filename or self.page.request.uri.split('/')[-1]
        if encoding:
            content = content.encode(encoding)
        filename = filename.replace(' ', '_').replace('/', '-').replace(':', '-').encode(encoding or 'ascii', 'ignore')
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

    def css3make(self, rounded=None, shadow=None, gradient=None, style=''):
        result = []
        if rounded:
            for x in rounded.split(','):
                if ':' in x:
                    side, r = x.split(':')
                else:
                    side, r = 'all', x
                side = side.lower()
                if side == 'all':
                    result.append('-moz-border-radius:%spx;' % r)
                    result.append('-webkit-border-radius:%spx;' % r)
                else:
                    if side in ('tl', 'topleft', 'top', 'left'):
                        result.append('-moz-border-radius-topleft:%spx;' % r)
                        result.append('-webkit-border-top-left-radius:%spx;' % r)
                    if side in ('tr', 'topright', 'top', 'right'):
                        result.append('-moz-border-radius-topright:%spx;' % r)
                        result.append('-webkit-border-top-right-radius:%spx;' % r)
                    if side in ('bl', 'bottomleft', 'bottom', 'left'):
                        result.append('-moz-border-radius-bottomleft:%spx;' % r)
                        result.append('-webkit-border-bottom-left-radius:%spx;' % r)
                    if side in ('br', 'bottomright', 'bottom', 'right'):
                        result.append('-moz-border-radius-bottomright:%spx;' % r)
                        result.append('-webkit-border-bottom-right-radius:%spx;' % r)
        if shadow:
            x, y, blur, color = shadow.split(',')
            result.append('-moz-box-shadow:%spx %spx %spx %s;' % (x, y, blur, color))
            result.append('-webkit-box-shadow:%spx %spx %spx %s;' % (x, y, blur, color))
            #if gradient:
            #
            #
            # background-image:-webkit-gradient(linear, 0% 0%, 0% 90%, from(rgba(16,96,192,0.75)), to(rgba(96,192,255,0.9)));
            #    background-image:-moz-linear-gradient(top,bottom,from(rgba(16,96,192,0.75)), to(rgba(96,192,255,0.9)));
            #    result.append('background-image:-moz-linear-gradient(top,bottom,from(rgba(16,96,192,0.75)), to(rgba(96,192,255,0.9)));')
            #    result.append('-webkit-box-shadow:%spx %spx %spx %s;'%(x,y,blur,color))
            #    # -moz-linear-gradient( [<point> || <angle>,]? <stop>, <stop> [, <stop>]* )
            # -moz-radial-gradient( [<position> || <angle>,]? [<shape> || <size>,]? <stop>, <stop>[, <stop>]* )
            #
            # -moz-linear-gradient (%(begin)s, %(from)s, %(to)s);
            # -webkit-gradient (%(mode)s, %(begin)s, %(end)s, from(%(from)s), to(%(to)s));
            #
        return '%s\n%s' % ('\n'.join(result), style)


    @public_method
    def tableImporterCheck(self,table=None,file_path=None,limit=None,**kwargs):
        result = Bag()

        result['imported_file_path'] = file_path
        reader = self.getReader(file_path)
        columns = Bag()
        rows = Bag()
        match_data = Bag()
        result['columns'] = columns
        result['rows'] = rows
        result['match_data'] = match_data
        table_col_list = []
        legacy_match = dict()
        if table:
            tblobj = self.page.db.table(table)
            for colname,colobj in tblobj.model.columns.items():
                table_col_list.append(colname)
                if colobj.attributes.get('legacy_name'):
                    legacy_match[colobj.attributes['legacy_name']] = colname
            result['methodlist'] = ','.join([k[9:] for k in dir(tblobj) if k.startswith('importer_')])
        for k,i in sorted(reader.index.items(),key=lambda tup:tup[1]):
            columns.setItem(k,None,name=reader.headers[i],field=k,width='10em')
            if k in table_col_list:
                dest_field = k 
                do_import = True
            elif k in legacy_match:
                dest_field = legacy_match[k]
                do_import = True
            else:
                dest_field = None
                do_import = not table
            match_data.setItem(k,Bag(dict(do_import=do_import,source_field=k,dest_field=dest_field)))
        for i,r in enumerate(reader()):
            if limit and i>=limit:
                break
            rows.setItem('r_%i' %i,Bag(dict(r)))
        return result.toXml()


    @public_method
    def tableImporterRun(self,table=None,file_path=None,match_index=None,import_method=None,no_trigger=None,**kwargs):
        tblobj = self.page.db.table(table)
        docommit = False
        reader = self.getReader(file_path)
        if import_method:
            handler = getattr(tblobj,'importer_%s' %import_method)
            return handler(reader)
        elif match_index:
            l = []
            for row in reader():
                r = {v:row[k] for k,v in match_index.items() if v is not ''}
                tblobj.recordCoerceTypes(r)
                if not no_trigger:
                    tblobj.insert(r)
                    docommit = True
                else:
                    l.append(r)
            if l:
                tblobj.insertMany(l)
                docommit = True
            if docommit:
                self.page.db.commit()
            return 'OK'

    def getReader(self,file_path):
        filename,ext = os.path.splitext(file_path)
        if ext=='.xls':
            reader = XlsReader(file_path)
        else:
            reader = CsvReader(file_path)
        reader.index = {self._importer_keycb(k):v for k,v in reader.index.items()}
        return reader


    def _importer_keycb(self,k):
        return slugify(str(k),sep='_')

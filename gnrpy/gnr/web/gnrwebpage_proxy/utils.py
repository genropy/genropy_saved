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

EXPORT_PDF_TEMPLATE = """
<html lang="en">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<title>%(title)s</title>
<meta name="author" content="GenroPy">
<style>%(style)s</style>
</head>
<body>
    %(body)s
</body>
</html>
"""

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

    def quickThermo(self,iterator,path=None,maxidx=None,labelfield=None,
                    labelcb=None,thermo_width=None,interval=None,title=None):
        path = path or 'gnr.lockScreen.thermo'
        lbl = ''
        if isinstance(iterator,list):
            maxidx = len(iterator)
        interval = 1
        if maxidx and maxidx >1000:
            interval = maxidx/100
        
        thermo = """<div class="quickthermo_box"> <div class="form_waiting"></div> </div>""" 
        title = """<div class="quickthermo_title">%s</div>""" %title if title else ""
        for idx,v in enumerate(iterator):
            if labelfield:
                if labelfield in v:
                    lbl = v[labelfield]
                else:
                    lbl = '%s %s' %(labelfield,idx)
            elif labelcb:
                lbl = labelcb(v)
            if idx % interval == 0:
                themropars = dict(maxidx=maxidx,idx=idx,lbl=lbl or 'item %s' %idx,thermo_width=thermo_width or '12em',
                                title=title)
                if maxidx:
                    thermo = r"""<div class="quickthermo_box"> %(title)s <progress style="width:%(thermo_width)s" max="%(maxidx)s" value="%(idx)s"></progress> <div class="quickthermo_caption">%(idx)s/%(maxidx)s - %(lbl)s</div></div>""" %themropars
                else:
                    thermo = """<div class="quickthermo_box"> %(title)s <div class="form_waiting"></div> <div class="quickthermo_caption">%(idx)s - %(lbl)s</div> </div>"""  %themropars
                self.page.setInClientData(path,thermo,idx=idx,maxidx=maxidx,lbl=lbl)
            yield v
        self.page.setInClientData(path,thermo,idx=maxidx,maxidx=maxidx,lbl=lbl)

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

        return '%s\n%s' % ('\n'.join(result), style)

    @public_method
    def tableImporterCheck(self,table=None,file_path=None,limit=None,importerStructure=None,checkCb=None,filetype=None,**kwargs):
        result = Bag()
        result['imported_file_path'] = file_path
        if table:
            importerStructure = importerStructure or self.page.db.table(table).importerStructure()
            checkCb = checkCb or self.page.db.table(table).importerCheck
        reader = self.getReader(file_path,filetype=filetype)
        importerStructure = importerStructure or dict()
        mainsheet = importerStructure.get('mainsheet')
        if mainsheet is None and importerStructure.get('sheets'):
            mainsheet = importerStructure.get('sheets')[0]['sheet']
        if checkCb:
            errormessage = checkCb(reader)
            if errormessage:
                result['errors'] = errormessage
                return result.toXml()
        if mainsheet is not None:
            reader.setMainSheet(mainsheet)
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
            columns.setItem(k,None,name=k,field=k,width='10em')
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
    def tableImporterRun(self,table=None,file_path=None,match_index=None,import_method=None,sql_mode=None,filetype=None,**kwargs):
        tblobj = self.page.db.table(table)
        docommit = False
        importerStructure = tblobj.importerStructure() or dict()
        reader = self.getReader(file_path,filetype=filetype)
        if importerStructure:
            sheets = importerStructure.get('sheets')
            if not sheets:
                sheets = [dict(sheet=importerStructure.get('mainsheet'),struct=importerStructure)]
            results = []
            for sheet in sheets:
                if sheet.get('sheet') is not None:
                    reader.setMainSheet(sheet['sheet'])
                struct = sheet['struct']
                match_index = tblobj.importerMatchIndex(reader,struct=struct)
                res = self.defaultMatchImporterXls(tblobj=tblobj,reader=reader,
                                                match_index=match_index,
                                                sql_mode=sql_mode,constants=struct.get('constants'),
                                                mandatories=struct.get('mandatories'))
                results.append(res)
                errors = filter(lambda r: r!='OK', results)
                if errors:
                    return 'ER'
        elif import_method:
            handler = getattr(tblobj,'importer_%s' %import_method)
            return handler(reader)
        
        if match_index:
            return self.defaultMatchImporterXls(tblobj=tblobj,reader=reader,
                                                    match_index=match_index,
                                                    sql_mode=sql_mode)

    def defaultMatchImporterXls(self,tblobj=None,reader=None,match_index=None,sql_mode=None,constants=None,mandatories=None):
        rows = self.adaptedRecords(tblobj=tblobj,reader=reader,match_index=match_index,sql_mode=sql_mode,constants=constants)
        docommit = False
        if sql_mode:
            rows_to_insert = list(rows)
            if rows_to_insert:
                tblobj.insertMany(rows_to_insert)
                docommit=True
        else:
            for r in rows:
                tblobj.importerInsertRow(r)
                docommit=True
        if docommit:
            self.page.db.commit()
        return 'OK'
    
    def adaptedRecords(self,tblobj=None,reader=None,match_index=None,sql_mode=None,constants=None):
        for row in self.quickThermo(reader(),maxidx=reader.nrows if hasattr(reader,'nrows') else None,
                        labelfield=tblobj.attributes.get('caption_field') or tblobj.name):
            r = constants or {}
            f =  {v:row[k] for k,v in match_index.items() if v is not ''}
            r.update(f)
            tblobj.recordCoerceTypes(r)
            if sql_mode:
                tpkey = tblobj.pkey
                if not r.get(tpkey):
                    r[tpkey] = tblobj.newPkeyValue(r)
            yield r
            

    def getReader(self,file_path,filetype=None,**kwargs):
        filename,ext = os.path.splitext(file_path)
        if filetype=='excel' or not filetype and ext in ('.xls','.xlsx'):
            reader = XlsReader(file_path,**kwargs)
        else:
            dialect = None
            if filetype=='tab':
                dialect = 'excel-tab'
            reader = CsvReader(file_path,dialect=dialect,**kwargs)
            reader.index = {self._importer_keycb(k):v for k,v in reader.index.items()}
        return reader


    def _importer_keycb(self,k):
        return slugify(str(k),sep='_')

    @public_method
    def exportPdfFromNodes(self,pages=None,name=None,
                            style=None,
                            orientation=None):
        style = style or ''
        name = name or self.page.getUuid()
        pdf_list = []
        print_handler = self.page.site.getService('print')
        pl = [name]
        pl.append('pdf')
        pl.append('%s.pdf' %name)
        outputFilePath = self.page.site.getStaticPath('page:exportPdfFromNodes',*pl,autocreate=-1)
        for i,p in enumerate(pages):
            hp = [name]
            hp.append('html')
            hp.append('page_%s.pdf' %i)
            page_path = self.page.site.getStaticPath('page:exportPdfFromNodes',*hp,autocreate=-1)
            print_handler.htmlToPdf(EXPORT_PDF_TEMPLATE %dict(title='%s %i' %(name,i) ,style=style, body=p),page_path, orientation=orientation)
            pdf_list.append(page_path)
        print_handler.getPrinterConnection('PDF').printPdf(pdf_list, 'export_%s' %name,
                                       outputFilePath=os.path.splitext(outputFilePath)[0])
        self.page.setInClientData(path='gnr.clientprint',
                                  value=self.page.site.getStaticUrl('page:exportPdfFromNodes',*pl, nocache=True),
                                  fired=True)
        

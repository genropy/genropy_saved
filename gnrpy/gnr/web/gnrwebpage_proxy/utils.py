#!/usr/bin/env pythonw
# -*- coding: utf-8 -*-
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
from gnr.core.gnrdecorator import public_method,extract_kwargs
from gnr.core.gnrbag import Bag, DirectoryResolver
from gnr.core.gnrlist import getReader
from gnr.core.gnrstring import slugify
from gnr.core.gnrlang import gnrImport, objectExtract
from gnr.core.gnrclasses import GnrClassCatalog

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
        self.default_thermo_path = 'gnr.lockScreen.thermo'

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
        path = path or self.default_thermo_path
        lbl = ''
        if isinstance(iterator,list):
            maxidx = len(iterator)
        interval = 1
        if maxidx and maxidx >1000:
            interval = maxidx/100
        title = title or self.page.localize('!![en]Executing')
        thermo = """<div class="quickthermo_box"> <div class="form_waiting"></div> </div>""" 
        title = """<div class="quickthermo_title">%s</div>""" %title
        for idx,v in enumerate(iterator):
            if isinstance(v,basestring):
                if labelfield:
                    lbl = labelfield
                else:
                    lbl = v
            elif labelfield:
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
                    thermo = r"""<div class="quickthermo_box"> %(title)s <progress style="width:%(thermo_width)s;margin-left:10px;margin-right:10px;" max="%(maxidx)s" value="%(idx)s"></progress> <div class="quickthermo_caption">%(idx)s/%(maxidx)s - %(lbl)s</div></div>""" %themropars
                else:
                    thermo = """<div class="quickthermo_box"> %(title)s <div class="form_waiting"></div> <div class="quickthermo_caption">%(idx)s - %(lbl)s</div> </div>"""  %themropars
                self.page.setInClientData(path,thermo,idx=idx,maxidx=maxidx,lbl=lbl)
            yield v
        self.page.setInClientData(path,thermo,idx=maxidx,maxidx=maxidx,lbl=lbl)
    
    def thermoMessage(self,title=None,message=None):
        thermo = """<div class="quickthermo_box thermo_message"> 
                        <div class="quickthermo_title">%(title)s </div> 
                        <div class="form_waiting"></div>
                        <div class="quickthermo_caption">%(message)s</div> 
                    </div>"""  %dict(title=title,message=message)
        self.page.setInClientData(self.default_thermo_path,thermo)


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
        try:
            reader = self.getReader(file_path,filetype=filetype)
        except Exception as e:
            self.page.clientPublish('floating_message',message='Reader error %s' %str(e),messageType='error')

        
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
            sql_count = tblobj.query(ignorePartition=True,excludeDraft=False, excludeLogicalDeleted=False).count()
            result['sql_count'] = sql_count
            for colname,colobj in tblobj.model.columns.items():
                table_col_list.append(colname)
                if colobj.attributes.get('legacy_name'):
                    legacy_match[colobj.attributes['legacy_name']] = colname
            import_modes = []
            if sql_count:
                import_modes.append('replace:Replace (remove %i records)' %sql_count)
            import_modes.append('insert_only:Insert only')
            import_modes.append('insert_or_update:Insert or update')
            import_modes.append('update_only:Update only')
            result['import_modes'] = ','.join(import_modes)
            result['import_mode'] = 'insert_only'
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
    @extract_kwargs(constant=True)
    def tableImporterRun(self,table=None,file_path=None,match_index=None,import_mode=None,
                        import_method=None,sql_mode=None,filetype=None,constant_kwargs=None,**kwargs):
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
                constants = constant_kwargs 
                constants.update(struct.get('constants') or dict())
                res = self.defaultMatchImporterXls(tblobj=tblobj,reader=reader,
                                                match_index=match_index,
                                                import_mode=import_mode,
                                                sql_mode=sql_mode,constants=constants,
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
                                                    import_mode=import_mode,
                                                    sql_mode=sql_mode,
                                                    constants=constant_kwargs)

    def defaultMatchImporterXls(self,tblobj=None,reader=None,match_index=None,sql_mode=None,constants=None,mandatories=None, import_mode=None):
        rows = self.adaptedRecords(tblobj=tblobj,reader=reader,match_index=match_index,sql_mode=sql_mode,constants=constants)
        docommit = False
        if import_mode=='replace':
            tblobj.empty()
        if sql_mode:
            rows_to_insert = list(rows)
            if rows_to_insert:
                tblobj.insertMany(rows_to_insert)
                docommit=True
        elif import_mode=='update_only':
            _updater_keyfield = match_index.pop('_updater_keyfield',None)
            if not _updater_keyfield:
                return
            for r in rows:
                key = r.pop(_updater_keyfield)
                missing_keys = []
                updatekw = {_updater_keyfield:key,'raw':sql_mode,'ignoreMissing':True}
                with tblobj.recordToUpdate(**updatekw) as rec:
                    if rec is None:
                        missing_keys.append(key)
                    else:
                        docommit = True
                        rec.update(r)
                if missing_keys:
                    self.page.clientPublish('floating_message',message='Missing record to update %s' %','.join(missing_keys),
                                            messageType='warning')
        else:
            for r in rows:
                tblobj.importerInsertRow(r,import_mode=import_mode)
                docommit=True
        if docommit:
            self.page.db.commit()
       
        return 'OK'
    
    def adaptedRecords(self,tblobj=None,reader=None,match_index=None,sql_mode=None,constants=None):
        for row in self.quickThermo(reader(),maxidx=reader.nrows if hasattr(reader,'nrows') else None,
                        labelfield=tblobj.attributes.get('caption_field') or tblobj.name):
            r = dict(constants) if constants else dict()
            f =  {v:row[k] for k,v in match_index.items() if v != ''}
            r.update(f)
            tblobj.recordCoerceTypes(r)
            if sql_mode:
                tpkey = tblobj.pkey
                if not r.get(tpkey):
                    r[tpkey] = tblobj.newPkeyValue(r)
            yield r
            

    def getReader(self,file_path,filetype=None,**kwargs):
        readerfile = self.page.site.storageNode(file_path)
        with readerfile.local_path() as local_path:
            return getReader(file_path=local_path,filetype=filetype,**kwargs)

    @public_method
    def exportPdfFromNodes(self,pages=None,name=None,
                            style=None,
                            orientation=None):
        style = style or ''
        name = name or self.page.getUuid()
        pdf_list = []
        print_handler = self.page.site.getService('htmltopdf')
        pdf_handler = self.page.site.getService('pdf')
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
        pdf_handler.joinPdf(pdf_list,outputFilePath)
        self.page.setInClientData(path='gnr.clientprint',
                                  value=self.page.site.getStaticUrl('page:exportPdfFromNodes',*pl, nocache=True),
                                  fired=True)
        

    def _handleMenuMethods(self,result,tblobj=None,res_type=None,topic=None):
        tableMethods = objectExtract(tblobj,'{res_type}Menu_'.format(res_type=res_type))
        page = self.page
        table = tblobj.fullname
        pageMethods = objectExtract(self.page,'{res_type}Menu_'.format(res_type=res_type))
        catalog = GnrClassCatalog()
        def cb(k,handler):
            if not getattr(handler,'is_rpc',None):
                return
            tags = getattr(handler,'tags',None)
            if tags and not self.application.checkResourcePermission(tags, page.userTags):
                return
            permissions = getattr(handler, 'permissions', None)
            if permissions and not page.checkTablePermission(table=table,permissions=permissions):
                return
            handler_topic = getattr(handler, 'topic', None)
            if topic:
                if not handler_topic:
                    return
                handler_topic = set(handler_topic.split(','))
                if not set(topic.split(',')).intersection(handler_topic):
                    return
            elif handler_topic:
                return
            handler_kwargs = dict(caption=getattr(handler, 'caption', k),
                                    description = getattr(handler, 'description', ''),
                                    tip=getattr(handler, 'tip', None),
                                    disabled=getattr(handler,'disabled',None),
                                    askParameters=getattr(handler,'askParameters',None))
            for k,v in objectExtract(handler,'rpc_').items():
                handler_kwargs['rpc_{}'.format(k)] = v
            handler_kwargs['rpcmethod'] = catalog.asText(handler)
            result.addItem(k,None,**handler_kwargs)

        for k,handler in pageMethods.items():
            cb(k,handler)
        for k,handler in tableMethods.items():
            cb(k,handler)

    def tableScriptResourceMenu(self, table=None, res_type=None,module_parameters=None,topic=None):
        #pkg,tblname = table.split('.')
        page = self.page
        tblobj = page.db.table(table)
        pkg = tblobj.pkg.name
        tblname = tblobj.name
        result = Bag()
        if topic is True:
            topic = None
        self._handleMenuMethods(result,tblobj=tblobj, res_type=res_type,topic=topic)
        resources = page.site.resource_loader.resourcesAtPath(page=page,pkg=None,path='tables/_default/%s' % res_type)
        resources_pkg = page.site.resource_loader.resourcesAtPath(page=page,pkg=pkg, path='tables/%s/%s' % (tblname, res_type))
        resources_custom = page.site.resource_loader.resourcesAtPath(page=page, path='tables/_packages/%s/%s/%s' % (pkg,tblname, res_type))
        resources.update(resources_pkg)
        resources.update(resources_custom)
        forbiddenNodes = []
        module_parameters = module_parameters or []

        def cb(node, _pathlist=None,_menutopic=None):
            has_parameters = False
            if node.attr['file_ext'] == 'py':
                resmodule = gnrImport(node.attr['abs_path'])

                tags = getattr(resmodule, 'tags', '')
                permissions = getattr(resmodule, 'permissions', None)
                module_topic = getattr(resmodule, 'topic', None)
                if _menutopic:
                    if not module_topic:
                        return
                    module_topic = set(module_topic.split(','))
                    if not set(_menutopic.split(',')).intersection(module_topic):
                        return
                elif module_topic:
                    return
                if (tags and not page.application.checkResourcePermission(tags, page.userTags)) or \
                    permissions and not page.checkTablePermission(table=table,permissions=permissions):
                    if node.label == '_doc':
                        forbiddenNodes.append('.'.join(_pathlist))
                    return
                #needSelection = getattr(resmodule, 'needSelection', True)
                module_kwargs = dict(caption=getattr(resmodule, 'caption', node.label),
                                    description = getattr(resmodule, 'description', ''),
                                    tip=getattr(resmodule, 'tip', None))
                for mpar in module_parameters:
                    module_kwargs[mpar] = getattr(resmodule,mpar,None)
                if  node.label == '_doc':
                    result.setAttr('.'.join(_pathlist), dict(caption=module_kwargs['caption'], description=module_kwargs['description'], tags=tags,
                                                             has_parameters=has_parameters))
                else:
                    mainclass = getattr(resmodule, 'Main', None)
                    assert mainclass, 'Main class is mandatory in tablescript resource'
                    has_parameters = hasattr(mainclass, 'parameters_pane')
                    tip = module_kwargs.pop('tip',None)                   
                    result.setItem('.'.join(_pathlist + [node.label]), None,
                                   resource=node.attr['rel_path'][:-3], has_parameters=has_parameters,
                                   table=table,tip=tip,**module_kwargs)
        pl=[]     
        resources.walk(cb,_pathlist=pl,_menutopic=topic)
        if '_common' in result:
            n = result.popNode('_common')
            if len(result):
                result.setItem('r_zz',None,caption='-')
            result.setItem(n.label,n.value,n.attr)
        for forbidden in forbiddenNodes:
            result.pop(forbidden)
        return result
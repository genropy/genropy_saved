#!/usr/bin/env python
# encoding: utf-8
"""
gnrwebextra.py

Created by Saverio Porcari on 2009-07-08.
Copyright (c) 2009 __MyCompanyName__. All rights reserved.
"""

from gnr.core.gnrhtml import GnrHtmlBuilder
from gnr.core.gnrstring import toText


class BaseTableResource(object):
        
    def __init__(self, page=None, resource_table = None):
        self.page = page
        self.site = self.page.site
        self.locale = self.page.locale
        self.db = self.page.db
        self.resource_table = resource_table
        self.init()
        

    def staticUrl(self, path):
        #miki implementa qui il rimappaggio
        return path
        
    def outputDocName(self, record, ext=''):
        ext= ext or self.output_document_ext
        doc_name = '%s_%s' % (self.maintable_obj.name, self.maintable_obj.recordCaption(record))
        return doc_name
        
    def filePath(self, folder, filename):
        self.filePath=self.page.temporaryDocument(folder, filename)
    
    def fileUrl(self, folder, filename):
        self.fileUrl=self.page.temporaryDocumentUrl(folder, filename)
       
class HtmlResource(BaseTableResource):
    maintable=''
    encoding= 'utf-8'
    
    def init(self,**kwargs):
        self.maintable=self.maintable or self.resource_table
        self.maintable_obj=self.db.table(self.maintable)
        self.builder = GnrHtmlBuilder()
        self.body = self.builder.body
        
    def rpc_run(self,**kwargs):
        return self.getHtmlFromRecord(**kwargs)
        
    def field(self, path, default=None, locale=None,
                    format=None, mask=None):
        datanode=self.data.getNode(path, default)
        value = datanode.value
        attr=datanode.attr
        if value is None:
            value=default
        format= format or attr.get('format')
        mask= mask or attr.get('mask')
        return self.toText(value,locale,format, mask, self.encoding)

    def getData(self,path,default=None):
        wildchars = []
        if path[0] in wildchars:
            value='not yet implemented'
        else:
            value=self.data.getItem(path, default)
        return value
        
    def loadDatastore(self, record, table):
        self.data = self.db.table(table or self.maintable or self.resource_table).recordAs(record, mode='bag')

    def getHtmlFromRecord(self, record='', table=None, filename = None, folder=None):
        self.loadDatastore(record,table)
        self.main()
        return self.builder.toHtml()
        
    def toText(self, obj, locale=None, format=None, mask=None, encoding=None):
        locale = locale or self.locale
        encoding = locale or self.encoding
        return toText(obj, locale=locale, format=format, mask=mask, encoding=encoding)
        
    def getPdfFromRecord(self, record, table, filename = None, folder=None):
        self.loadDatastore(self,record,table)
        filename=filename or self.outputDocName(self.data)
        outputPath = self.filePath(filename, folder)
        self.builder.toPdf(outputPath)
        return outputPath
        
#!/usr/bin/env python
# encoding: utf-8
"""
gnrtablescript.py

Created by Saverio Porcari on 2009-07-08.
Copyright (c) 2009 __MyCompanyName__. All rights reserved.
"""
import os.path
from gnr.core.gnrhtml import GnrHtmlBuilder
from gnr.core.gnrstring import toText


class TableScript(object):
        
    def __init__(self, page=None, resource_table = None,db=None,locale='en',tempFolder='',**kwargs):
        if page:
            self.page = page
            self.site = self.page.site
            self.locale = self.page.locale
            self.db = self.page.db
            self.tempFolder = tempFolder or self.page.temporaryDocument()
        else:
            self.db=db
            self.locale=locale
            self.tempFolder = tempFolder
        self.resource_table = resource_table
        self.init(**kwargs)
        
    def filePath(self, filename, *folders):
        folders=folders or []
        if folders and folders[0] == '*temp':
            folders = list(folders)
            folders[0] = self.tempFolder
        
        return os.path.join(*(folders+[filename]))
    
    def fileUrl(self, folder, filename):
        return self.page.temporaryDocumentUrl(folder, filename)
        
class TableScriptOnRecord(TableScript):
    
    def field(self, path, default=None, locale=None,
                    format=None, mask=None):
        datanode=self._data.getNode(path, default)
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
            value=self._data.getItem(path, default)
        return value
        
    def loadRecord(self, record):
        self._data = self.db.table(self.maintable or self.resource_table).recordAs(record, mode='bag')
        
    def test(self):
        x=TableScriptOnRecord(mypage)
        
    
    def outputDocName(self, ext=''):
        maintable_obj = self.db.table(self.maintable)
        if ext and not ext[0]=='.':
            ext = '.%s' % ext
        doc_name = '%s_%s%s' % (maintable_obj.name, maintable_obj.recordCaption(self._data), ext)
        return doc_name
        
class RecordToHtml(TableScriptOnRecord):
    maintable=''
    destination_folder = '*temp'
    encoding= 'utf-8'
    
    def init(self,**kwargs):
        self.maintable=self.maintable or self.resource_table
        self.maintable_obj=self.db.table(self.maintable)
        self.builder = GnrHtmlBuilder()
        
        
    def rpc_run(self, record=None, filepath=None,rebuild=False, **kwargs):
        if not record:
            return
        self.loadRecord(record)
        filepath=filepath or self.filePath(self.outputDocName(ext='html'), self.destination_folder)
        if rebuild or not os.path.isfile(filepath):
            print 'createHtml'
            html=self.createHtml(filepath=filepath, **kwargs)
            
        else:
            print 'use cache'
            with open(filepath,'r') as f:
                html=f.read()
        return html
        
    def createHtml(self, filepath=None, **kwargs):
        self.initializeBuilder()
        self.main()
        self.builder.toHtml(filepath=filepath)
        return self.builder.html
        
    def initializeBuilder(self):
        self.builder.initializeSrc()
        self.body = self.builder.body
        self.builder.styleForLayout()
        
    #def getHtmlFromRecord(self, record='', table=None, filename = None, folder=None):
    #    folder = folder or '*temp'
    #    if not record:
    #        return None
    #    self.loadRecord(record)
    #    self.initializeBuilder()
    #    self.main()
    #    if filename:
    #        filename = self.filePath(folder, filename)
    #    return self.builder.toHtml(filename=filename)
        
    def toText(self, obj, locale=None, format=None, mask=None, encoding=None):
        locale = locale or self.locale
        encoding = locale or self.encoding
        return toText(obj, locale=locale, format=format, mask=mask, encoding=encoding)
        
    def getPdf(self, record='', table=None, filename = None, folder=None):
        folder = folder or '*temp'
        self.loadRecord(record)
        self.initializeBuilder()
        self.main()
        filename=filename or self.outputDocName(self.data, ext='.pdf')
        outputPath = self.filePath(filename, folder)
        self.builder.toPdf(outputPath)
        return outputPath

       
        
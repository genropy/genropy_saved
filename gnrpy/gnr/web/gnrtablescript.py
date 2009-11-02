#!/usr/bin/env python
# encoding: utf-8
"""
gnrtablescript.py

Created by Saverio Porcari on 2009-07-08.
Copyright (c) 2009 __MyCompanyName__. All rights reserved.
"""
import os.path
import tempfile
from gnr.core.gnrbag import Bag
from gnr.core.gnrhtml import GnrHtmlBuilder
from gnr.core.gnrstring import toText
from gnr.core.gnrlang import NotImplementedException


class TableScript(object):
        
    def __init__(self, page=None, resource_table = None,db=None,locale='en',tempFolder='',**kwargs):
        
        if page:
            self.page = page
            self.site = self.page.site
            self.locale = self.page.locale
            self.db = self.page.db
            self.docFolder = tempFolder or self.page.temporaryDocument()
        else:
            self.db=db
            self.locale=locale
            self.tempFolder = tempFolder
        self.resource_table = resource_table
        self.init(**kwargs)
        
    def __call__(self,  *args, **kwargs):
        raise NotImplementedException()
       
       
    def getFolderPath(self, *folders):
        folders=folders or []
        if folders and folders[0] == '*connections':
            folders = [self.page.connectionDocument(*list(folders[1:]+('',)))] 
        return os.path.join(*folders)
        
    def filePath(self, filename, *folders):
        return os.path.join(self.getFolderPath(*folders), filename)
        
    def fileUrl(self, folder, filename):
        return self.page.temporaryDocumentUrl(folder, filename)
        
class TableScriptOnRecord(TableScript):
    
    def __call__(self, record=None, **kwargs):
        raise NotImplementedException()
        
    def getData(self,path,default=None):
        wildchars = []
        if path[0] in wildchars:
            value='not yet implemented'
        else:
            value=self._data.getItem(path, default)
        return value
        
    def loadRecord(self, record=None,**kwargs):
        self._data = self.db.table(self.maintable or self.resource_table).recordAs(record, mode='bag')
        self.onRecordLoaded(**kwargs)  
        
    def onRecordLoaded(self,**kwargs):
        pass
    
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
    html_folder = '*connections/html'
    pdf_folder = '*connections/pdf'
    encoding= 'utf-8'
    
    def init(self,**kwargs):
        self.maintable=self.maintable or self.resource_table
        self.maintable_obj=self.db.table(self.maintable)
        self.builder = GnrHtmlBuilder()
        
    def __call__(self, record=None, filepath=None,
                       rebuild=False, dontSave=False, pdf=False, runKwargs=None,**kwargs):
        """This method returns the html corresponding to a given record.
           the html can be loaded from a cached document or created if still doesn't exist.
        """
        if not record:
            return
        self.loadRecord(record, **kwargs)
        if kwargs:
            self._data['kwargs']=Bag()
            for k,v in kwargs.items():
                self._data['kwargs.%s' % k] = v
           
            
        #if not (dontSave or pdf):
        self.filepath=filepath or os.path.join(self.hmtlFolderPath(),self.outputDocName(ext='html'))
        #else:
        #    self.filepath = None
        if rebuild or not os.path.isfile(self.filepath):
            html=self.createHtml(filepath=self.filepath , **kwargs)
            
        else:
            with open(self.filepath,'r') as f:
                html=f.read()
        if pdf:
            temp = tempfile.NamedTemporaryFile(suffix='.pdf')
            self.page.site.print_handler.htmlToPdf(self.filepath, temp.name)
            with open(temp.name,'rb') as f:
                html=f.read()
        return html
        
    def createHtml(self, filepath=None, **kwargs):
        #filepath = filepath or self.filepath
        self.initializeBuilder()
        self.main()
        self.builder.toHtml(filepath=filepath)
        return self.builder.html
        
    def initializeBuilder(self):
        self.builder.initializeSrc()
        self.body = self.builder.body
        self.builder.styleForLayout()
        
    def hmtlFolderPath(self):
        return self.getFolderPath(*self.html_folder.split('/'))
        
    def pdfFolderPath(self):
        return self.getFolderPath(*self.pdf_folder.split('/'))
        
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

    def toText(self, obj, locale=None, format=None, mask=None, encoding=None):
        locale = locale or self.locale
        encoding = locale or self.encoding
        return toText(obj, locale=locale, format=format, mask=mask, encoding=encoding)
        
    #def getPdf(self, record='', table=None, filename = None, folder=None):
    #    folder = folder or '*temp'
    #    self.loadRecord(record)
    #    self.initializeBuilder()
    #    self.main()
    #    filename=filename or self.outputDocName(self._data, ext='.pdf')
    #    outputPath = self.filePath(filename, folder)
    #    self.builder.toPdf(outputPath)
    #    return outputPath
    #
       
        
#!/usr/bin/env python
# encoding: utf-8
"""
gnrtablescript.py

Created by Saverio Porcari on 2009-07-08.
Copyright (c) 2009 __MyCompanyName__. All rights reserved.
"""

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
        
    def outputDocName(self, record, ext=''):
        ext= ext or self.output_document_ext
        doc_name = '%s_%s' % (self.maintable_obj.name, self.maintable_obj.recordCaption(record))
        return doc_name
        
    def filePath(self, filename, *folders):
        if folders and folders[0] == '*temp':
            folders = list(folders)
            folders[0] = self.tempFolder
        return os.path.join(*folders,filename)
    
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
       
        
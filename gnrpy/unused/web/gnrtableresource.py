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
    def __init__(self, page=None, resource_table=None, db=None, locale='en'):
        if page:
            self.page = page
            self.site = self.page.site
            self.locale = self.page.locale
            self.db = self.page.db
            self.resource_table = resource_table
        else:
            self.db = db
            self.locale = locale
        self.init()


    def staticUrl(self, path):
        #miki implementa qui il rimappaggio
        return path

    def outputDocName(self, record, ext=''):
        ext = ext or self.output_document_ext
        doc_name = '%s_%s' % (self.maintable_obj.name, self.maintable_obj.recordCaption(record))
        return doc_name

    def filePath(self, folder, filename):
        if hasattr(self, 'page'):
            return self.page.temporaryDocument(folder, filename)
        else:
            return filename

    def fileUrl(self, folder, filename):
        return self.page.temporaryDocumentUrl(folder, filename)
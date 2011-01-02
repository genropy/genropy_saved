#!/usr/bin/env python
# encoding: utf-8
"""
export.py

Created by Francesco Porcari on 2010-10-16.
Copyright (c) 2010 Softwell. All rights reserved.
"""
from gnr.web.batch.btcbase import BaseResourceBatch
from gnr.core.gnrxls import XlsWriter
from gnr.core.gnrstring import toText

class CsvWriter(object):
    """docstring for CsVWriter"""

    def __init__(self, columns=None, coltypes=None, headers=None, filepath=None):
        self.headers = headers
        self.columns = columns
        self.coltypes = coltypes
        self.filepath = filepath

    def writeHeaders(self):
        self.result = ['\t'.join(self.headers)]

    def cleanCol(self, txt, dtype):
        txt = txt.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ').replace('"', "'")
        if txt:
            if txt[0] in ('+', '=', '-'):
                txt = ' %s' % txt
            elif txt[0].isdigit() and (dtype in ('T', 'A', '', None)):
                txt = '%s' % txt # how to escape numbers in text columns?
        return txt

    def writeRow(self, row):
        self.result.append('\t'.join([self.cleanCol(toText(row.get(col)), self.coltypes[col]) for col in self.columns]))

    def workbookSave(self):
        f = open('%s.csv' % self.filepath, 'w')
        result = '\n'.join(self.result)
        f.write(result.encode('utf-8'))
        f.close()

class BaseResourceExport(BaseResourceBatch):
    def __init__(self, *args, **kwargs):
        super(BaseResourceExport, self).__init__(*args, **kwargs)
        self.locale = self.page.locale
        self.columns = []
        self.headers = []
        self.coltypes = {}
        self.data = None

    def gridcall(self, data=None, struct=None, export_mode=None, datamode=None):
        self.batch_parameters = dict(export_mode=export_mode, filename=None)

        self.prepareFromStruct(struct)
        self.data = self.rowFromValue(data) if datamode == 'bag' else self.rowFromAttr(data)
        self._pre_process()
        self.do()
        return self.fileurl

    def rowFromAttr(self, data):
        for r in data:
            yield r.getAttr()

    def rowFromValue(self, data):
        for r in data:
            yield r.getValue()

    def prepareFromStruct(self, struct=None):
        for view in struct.values():
            for row in view.values():
                for cell in row:
                    col = self.db.colToAs(cell.getAttr('field'))
                    self.columns.append(col)
                    self.headers.append(cell.getAttr('name'))
                    self.coltypes[col] = cell.getAttr('dtype')

    def _pre_process(self):
        self.pre_process()
        self.fileurl = None
        self.export_mode = self.batch_parameters['export_mode']
        self.prepareFilePath(self.batch_parameters['filename'])
        if not self.data:
            selection = self.get_selection()
            struct = self.batch_parameters.get('struct')
            self.data = self.btc.thermo_wrapper(selection.data, message=self.tblobj.name_plural, tblobj=self.tblobj)
            if not struct:
                self.columns = selection.columns
                self.columns = [c for c in self.columns if not c in ('pkey', 'rowidx')]
                self.coltypes = dict([(k, v['dataType']) for k, v in selection.colAttrs.items()])
                self.headers = selection.colHeaders
            else:
                self.prepareFromStruct(struct)
        writerPars = dict(columns=self.columns, coltypes=self.coltypes, headers=self.headers,
                          filepath=self.filepath, locale=self.locale)
        if self.export_mode == 'xls':
            self.writer = XlsWriter(**writerPars)
        elif self.export_mode == 'csv':
            self.writer = CsvWriter(**writerPars)


    def do(self):
        self.writer.writeHeaders()
        for row in self.data:
            self.writer.writeRow(row)
        self.post_process()

    def post_process(self):
        self.writer.workbookSave()
        self.fileurl = self.page.site.getStaticUrl('page:output', self.export_mode,
                                                   '%s.%s' % (self.filename, self.export_mode), nocache=True,
                                                   download=True)

    def prepareFilePath(self, filename=None):
        if not filename:
            filename = self.maintable.replace('.', '_') if hasattr(self, 'maintable') else self.page.getUuid()
        filename = filename.replace(' ', '_').replace('.', '_').replace('/', '_')[:64]
        filename = filename.encode('ascii', 'ignore')
        self.filename = filename
        self.filepath = self.page.site.getStaticPath('page:output', self.export_mode, self.filename, autocreate=-1)

    def result_handler(self):
        return 'Execution completed', dict(url=self.fileurl, document_name=self.batch_parameters['filename'])

    def get_record_caption(self, item, progress, maximum, **kwargs):
        caption = '%s (%i/%i)' % (self.tblobj.recordCaption(item),
                                  progress, maximum)
        return caption

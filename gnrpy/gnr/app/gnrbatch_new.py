#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  gnrbatch_new.py
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#

from time import time
from collections import defaultdict
import os

class GnrBatch(object):
    def __init__(self, data=None, runKwargs=None, **kwargs):
        self.runKwargs = runKwargs.asDict(True) if runKwargs else {}
        self.data = data
        for k, v in kwargs.items():
            if v:
                setattr(self, k, v)
                
    def set_data(self, data):
        self.data = data
        
    def data_counter(self):
        return len(self.data)
        
    def data_fetcher(self):
        for item in self.data:
            yield item
            
    def pre_process(self):
        pass
        
    def process_chunk(self, chunk):
        pass
        
    def post_process(self):
        pass
        
    def collect_result(self):
        pass
        
    def run(self):
        self.progress = 0
        self.page.btc.thermo_line_update(line='batch_steps', maximum=5, progress=2, message='!!Pre processing')
        self.pre_process()
        self.page.btc.thermo_line_update(line='batch_steps', maximum=5, progress=3, message='!!Executing')
        self.process()
        self.page.btc.thermo_line_update(line='batch_steps', maximum=5, progress=4, message='!!Post processing')
        
        self.post_process()
        self.page.btc.thermo_line_update(line='batch_steps', maximum=5, progress=5, message='!!Collecting results')
        
        result = self.collect_result()
        return result
        
    def process(self):
        self.thermo_start(line='batch_main', msg='')
        for chunk in self.data_fetcher():
            self.thermo_step(line='batch_main', chunk=chunk)
            self.process_chunk(chunk, **self.runKwargs)
            self.progress += 1
            
    def thermo_start(self, line=None, msg=None):
        self.page.btc.thermo_line_start(line=line, maximum=len(self.data),
                                        message=msg)
                                        
    def thermo_step(self, line=None, chunk=None):
        self.page.btc.thermo_line_update(line=line, maximum=len(self.data),
                                         message=self.thermo_chunk_message(chunk),
                                         progress=self.progress)
                                         
    def thermo_chunk_message(self, chunk, row):
        pass
        
class SelectionToXls(GnrBatch):
    def __init__(self, data=None, table=None, filename=None, columns=None, locale=None, **kwargs):
        if columns:
            columns = columns.split(',')
        else:
            columns = data.columns
        self.colHeaders = {}
        if('structure') in kwargs:
            self.colHeaders = dict([(x.replace('.', '_').replace('@', '_').replace('$', ''), y) for x, y in
                                    kwargs['structure']['#0.#0'].digest('#a.field,#a.name') if (x and y)])
            columns = [c for c in columns if c in self.colHeaders]
        self.columns = columns
        self.locale = locale
        self.filename = filename or '%s.xls' % table.replace('.', '_')
        self.colAttrs = data.colAttrs
        data = data.output('dictlist', columns=self.columns, locale=self.locale)
        super(SelectionToXls, self).__init__(data=data, **kwargs)
        self.tblobj = self.page.db.table(table)
        self.batch_prefix = 'exp_%s' % self.tblobj.name
        self.batch_title = "Exporting %s" % self.tblobj.name
        self.batch_thermo_lines = 'row'
        self.batch_note = "Exporting %s" % self.tblobj.name
        self.batch_cancellable = False
        self.batch_delay = 0.5
        
        #self.thermo_maximum[0] = self.data_counter()
        
    def thermo_chunk_message(self, chunk):
        return self.tblobj.recordCaption(chunk)
        
    def pre_process(self):
        import xlwt
        
        self.workbook = xlwt.Workbook(encoding='latin-1')
        self.sheet = self.workbook.add_sheet(self.filename)
        float_style = xlwt.XFStyle()
        float_style.num_format_str = '#,##0.00'
        int_style = xlwt.XFStyle()
        int_style.num_format_str = '#,##0'
        font0 = xlwt.Font()
        font0.name = 'Times New Roman'
        font0.bold = True
        hstyle = xlwt.XFStyle()
        hstyle.font = font0
        for c, header in enumerate(self.columns):
            self.sheet.write(0, c, self.colHeaders[header], hstyle)
        self.current_row = 1
        
    def process_chunk(self, chunk):
        for c, column in enumerate(self.columns):
            if isinstance(chunk[column], list):
                value = ','.join([str(x != None and x or '') for x in chunk[column]])
            else:
                value = chunk[column]
            self.sheet.write(self.current_row, c, value)
        self.current_row += 1
        
    def post_process(self):
        self.filePath = self.page.temporaryDocument(self.filename)
        self.fileUrl = self.page.temporaryDocumentUrl(self.filename)
        self.workbook.save(self.filePath)
        
    def collect_result(self):
        return self.fileUrl
        
class PrintDbData(GnrBatch):
    def __init__(self, table=None, table_resource=None, class_name=None, selection=None,
                 folder=None, printParams=None, pdfParams=None, commitAfterPrint=False, batch_note=None, **kwargs):
        #import cups
        
        super(PrintDbData, self).__init__(**kwargs)
        self.htmlMaker = self.page.site.loadTableScript(page=self.page, table=table,
                                                        respath=table_resource,
                                                        class_name=class_name)
        self.htmlMaker.parentBatch = self
        self.table = table
        self.folder = folder or self.htmlMaker.pdfFolderPath()
        if pdfParams:
            self.printer_name = 'PDF'
            printParams = pdfParams
            self.outputFilePath = self.page.userDocument('output', 'pdf', self.docName)
        else:
            self.printer_name = printParams.pop('printer_name')
            self.outputFilePath = None
        self.print_handler = self.page.getService('print')
        self.print_connection = self.print_handler.getPrinterConnection(self.printer_name, printParams)
        self.file_list = []
        self.commitAfterPrint = commitAfterPrint
        self.batch_note = batch_note
        
    @property
    def batch_prefix(self):
        """TODO"""
        return self.htmlMaker.batch_prefix
        
    @property
    def batch_title(self):
        """TODO"""
        return self.htmlMaker.batch_title
        
    @property
    def batch_delay(self):
        """TODO"""
        return self.htmlMaker.batch_delay
        
    @property
    def batch_cancellable(self):
        """TODO"""
        return self.htmlMaker.batch_cancellable
        
    @property
    def batch_thermo_lines(self):
        """TODO"""
        return self.htmlMaker.batch_thermo_lines
        
    def collect_result(self):
        filename = None
        if self.file_list:
            filename = self.print_connection.printFiles(self.file_list, 'GenroPrint',
                                                        outputFilePath=self.outputFilePath)
        if filename:
            return self.page.userDocumentUrl('output', 'pdf', filename)
            
    def process_chunk(self, chunk, **kwargs):
        html = self.htmlMaker(chunk['pkey'], rebuild=self.rebuild, **kwargs)
        if self.htmlMaker.page_height<self.htmlMaker.page_width:
            orientation='Landscape'
        else:
            orientation='Portrait'
        if html != False:
            self.file_list.append(self.print_handler.htmlToPdf(self.htmlMaker.filepath, self.folder, orientation=orientation))
            
    def thermo_chunk_message(self, chunk):
        return self.data.dbtable.recordCaption(chunk)
        
    def data_fetcher(self):     ##### Rivedere per passare le colonne
        for row in self.data.output('dictlist'):
            yield row
            
    def post_process(self):
        if self.commitAfterPrint:
            self.page.db.commit()
            
class PrintSelection(PrintDbData):
    pass
    
class PrintRecord(PrintDbData):
    def process(self):
        self.process_chunk(dict(pkey=self.data), **self.runKwargs)
        
class MailSender(GnrBatch):
    def __init__(self, page=None, table=None, doctemplate=None, selection=None,
                 cc_address=None, bcc_address=None, from_address=None, to_address=None, attachments=None,
                 account=None, host=None, port=None, user=None, password=None, ssl=None, tls=None,
                 **kwargs):
        super(MailSender, self).__init__(**kwargs)
        self.data = selection
        self.page = page
        self.doctemplate = doctemplate
        self.tblobj = self.page.db.table(table)
        self.from_address = from_address
        self.mail_handler = self.page.getService('mail')
        self.cc_address = cc_address
        self.bcc_address = bcc_address
        self.attachments = attachments
        self.account = account
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.ssl = ssl
        self.tls = tls
        self.to_address = to_address
        
    def data_fetcher(self):
        for row in self.data.output('records'):
            yield row
            
    def process_chunk(self, chunk, **kwargs):
        print x
        self.mail_handler.sendmail_template(chunk,
                                            to_address=self.to_address or chunk[self.doctemplate['meta.to_address']],
                                            body=self.doctemplate['content'], subject=self.doctemplate['meta.subject'],
                                            cc_address=self.cc_address, bcc_address=self.bcc_address,
                                            from_address=self.from_address,
                                            attachments=self.attachments, account=self.accont,
                                            host=self.host, port=self.port, user=self.user, password=self.password,
                                            ssl=self.ssl, tls=self.tls, html=True, async=True)
                                            
################################
class Fake(GnrBatch):
    thermo_rows = 2
        
    def __init__(self, **kwargs):
        super(Fake, self).__init__(**kwargs)
        self.thermo_maximum[1] = 1000
        self.thermo_maximum[2] = 1000
        
    def data_fetcher(self):     ##### Rivedere per passare le colonne
        for row in range(1000):
            yield row
            
    def process_chunk(self, chunk):
        i = 0
        self.thermo_step(row=2, status=0)
        for subrow in range(1000):
            self.thermo_step(row=2, message='fake %i/%i' % (chunk, subrow))
            
    def collect_result(self):
        pass
        
    ##################################
        
class ProgressThermo(object):
    def __init__(self, name, lines=None, **kwargs):
        self.name = name
        self.lines = lines
        self.lines.update(dict([(k[8:], dict(maximum=v)) for k, v in kwargs.items() if k.startswith('maximum_')]))
        
    def setLine(self, line, **kwargs):
        self.lines[line].update(kwargs)
           
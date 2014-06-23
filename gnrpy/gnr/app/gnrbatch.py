#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  gnrbatch.py
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.

'''
Character width dictionary and convenience functions for column sizing
with xlwt when Arial 10 is the standard font. Widths were determined
experimentally using Excel 2000 on Windows XP. I have no idea how well
these will work on other setups. For example, I don't know if system
video settings will affect the results. I do know for sure that this
module won't be applicable to other fonts in general.

//John Yeung  2009-09-02
'''

from time import time
from collections import defaultdict
import os
import datetime

charwidths = {
    '0': 262.637, '1': 262.637, '2': 262.637, '3': 262.637, '4': 262.637, '5': 262.637, '6': 262.637,
    '7': 262.637, '8': 262.637, '9': 262.637, 'a': 262.637, 'b': 262.637, 'c': 262.637, 'd': 262.637,
    'e': 262.637, 'f': 146.015, 'g': 262.637, 'h': 262.637, 'i': 117.096, 'j': 88.178, 'k': 233.244,
    'l': 88.178, 'm': 379.259, 'n': 262.637, 'o': 262.637, 'p': 262.637, 'q': 262.637, 'r': 175.407,
    's': 233.244, 't': 117.096, 'u': 262.637, 'v': 203.852, 'w': 321.422, 'x': 203.852, 'y': 262.637,
    'z': 233.244, 'A': 321.422, 'B': 321.422, 'C': 350.341, 'D': 350.341, 'E': 321.422, 'F': 291.556,
    'G': 350.341, 'H': 321.422, 'I': 146.015, 'J': 262.637, 'K': 321.422, 'L': 262.637, 'M': 379.259,
    'N': 321.422, 'O': 350.341, 'P': 321.422, 'Q': 350.341, 'R': 321.422, 'S': 321.422, 'T': 262.637,
    'U': 321.422, 'V': 321.422, 'W': 496.356, 'X': 321.422, 'Y': 321.422, 'Z': 262.637, ' ': 146.015,
    '!': 146.015, '"': 175.407, '#': 262.637, '$': 262.637, '%': 438.044, '&': 321.422, '\'': 88.178,
    '(': 175.407, ')': 175.407, '*': 203.852, '+': 291.556, ',': 146.015, '-': 175.407, '.': 146.015,
    '/': 146.015, ':': 146.015, ';': 146.015, '<': 291.556, '=': 291.556, '>': 291.556, '?': 262.637,
    '@': 496.356, '[': 146.015, '\\': 146.015, ']': 146.015, '^': 203.852, '_': 262.637, '`': 175.407,
    '{': 175.407, '|': 146.015, '}': 175.407, '~': 291.556}
    
def colwidth(n):
    '''Translate human-readable units to BIFF column width units'''
    if n <= 0:
        return 0
    if n <= 1:
        return n * 456
    return 200 + n * 256
    
def fitwidth(data, bold=False):
    '''Try to autofit Arial 10'''
    units = 220
    for char in unicode(data):
        if char in charwidths:
            units += charwidths[char]
        else:
            units += charwidths['0']
    if bold:
        units *= 1.1
    return max(units, 700) # Don't go smaller than a reported width of 2
    
class GnrBatch(object):
    thermo_rows = 1
    
    def __init__(self, data=None, runKwargs=None, thermocb=None, thermoId=None, thermofield='*', thermodelay=0.5,
                 **kwargs):
        self.thermocb = thermocb or (lambda *a, **kw:None)
        self.thermoId = thermoId
        self.thermodelay = thermodelay
        self.thermofield = thermofield
        self.last_thermotime = time()
        self.stopped = False
        self.thermo_status = defaultdict(lambda: 0)
        self.thermo_message = defaultdict(lambda: '')
        self.thermo_maximum = defaultdict(lambda: None)
        self.thermo_indeterminate = defaultdict(lambda: None)
        self.runKwargs = runKwargs.asDict(True) if runKwargs else {}
        self.data = data
        for k, v in kwargs.items():
            if v:
                setattr(self, k, v)
                
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
        self.thermo_init()
        self.pre_process()
        self.process()
        self.post_process()
        result = self.collect_result()
        self.thermo_end()
        return result
        
    def process(self):
        for chunk in self.data_fetcher():
            self.thermo_step(chunk)
            if self.stopped:
                break
            self.process_chunk(chunk, **self.runKwargs)
            
    def thermo_init(self, row=None):
        if self.thermoId:
            kwargs = dict()
            rows = row and [row] or range(self.thermo_rows)
            for i in rows:
                j = i + 1
                kwargs['progress_%i' % j] = self.thermo_status[j]
                kwargs['message_%i' % j] = self.thermo_message[j]
                kwargs['maximum_%i' % j] = self.thermo_maximum[j]
                kwargs['indeterminate_%i' % j] = self.thermo_indeterminate[j]
            if row is not None:
                self.thermocb(self.thermoId, **kwargs)
            else:
                self.thermocb(self.thermoId, command='init', **kwargs)
                
    def thermo_reset(self, row, max_value):
        kwargs = dict()
        self.thermo_maximum[row] = max_value
        kwargs['maximum_%i' % row] = max_value
        self.thermo_status[row] = 0
        kwargs['progress_%i' % row] = self.thermo_status[row]
        self.last_thermotime = time()
        return self.thermocb(self.thermoId, **kwargs)
        
    def thermo_step(self, chunk=None, row=1, status=None, message=None, step=1):
        kwargs = dict()
        if status is not None:
            self.thermo_status[row] = status
        else:
            self.thermo_status[row] += step
        if self.thermoId:
            if time() - self.last_thermotime >= self.thermodelay:
                self.last_thermotime = time()
                kwargs['progress_%i' % row] = self.thermo_status[row]
                kwargs['message_%i' % row] = message or self.thermo_chunk_message(chunk=chunk, row=row)
                result = self.thermocb(self.thermoId, **kwargs)
                if result == 'stop':
                    self.stopped = True
                    self.thermocb(self.thermoId, command='stopped')
                return result
                
    def thermo_chunk_message(self, chunk, row):
        pass
        
    def thermo_end(self):
        if self.thermoId:
            self.thermocb(self.thermoId, command='end')
            
class SelectionToXls(GnrBatch):
    def __init__(self, data=None, table=None, filename=None, columns=None, locale=None, **kwargs):
        if columns:
            columns = columns.split(',')
        elif data:
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
        self.thermo_maximum[0] = self.data_counter()
        self.colsizes = dict()
        
    def thermo_chunk_message(self, chunk, row):
        if self.thermofield == '*':
            msg = self.tblobj.recordCaption(chunk)
        else:
            msg = chunk[self.thermofield]
        return msg
        
    def pre_process(self):
        import xlwt
        
        self.workbook = xlwt.Workbook(encoding='latin-1')
        self.sheet = self.workbook.add_sheet(self.filename)
        self.float_style = xlwt.XFStyle()
        self.float_style.num_format_str = '#,##0.00'
        self.int_style = xlwt.XFStyle()
        self.int_style.num_format_str = '#,##0'
        self.date_style = xlwt.XFStyle()
        self.date_style.num_format_str = 'DD-MM-YYYY'
        font0 = xlwt.Font()
        font0.name = 'Times New Roman'
        font0.bold = True
        hstyle = xlwt.XFStyle()
        hstyle.font = font0
        for c, header in enumerate(self.columns):
            self.sheet.write(0, c, self.colHeaders[header], hstyle)
            self.colsizes[c] = max(self.colsizes.get(c, 0), fitwidth(unicode(self.colHeaders[header])))
        self.current_row = 1
        
    def process_chunk(self, chunk):
        for c, column in enumerate(self.columns):
            if isinstance(chunk[column], list):
                value = ','.join([str(x != None and x or '') for x in chunk[column]])
            else:
                value = chunk[column]
            if type(value) == int:
                style = self.int_style
            elif type(value) == float:
                style = self.float_style
            elif type(value) == datetime.date:
                style = self.date_style
            else:
                style = None
                self.colsizes[c] = max(self.colsizes.get(c, 0), fitwidth(unicode(value)))
            if style:
                self.sheet.write(self.current_row, c, value, style)
            else:
                self.sheet.write(self.current_row, c, value)
        self.current_row += 1
        
    def post_process(self):
        for colindex, colsize in self.colsizes.items():
            self.sheet.col(colindex).width = colsize
        self.filePath = self.page.temporaryDocument(self.filename)
        self.fileUrl = self.page.temporaryDocumentUrl(self.filename)
        self.workbook.save(self.filePath)
        
    def collect_result(self):
        return self.fileUrl
        
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
        self.mail_handler.sendmail_template(chunk,
                                            to_address=self.to_address or chunk[self.doctemplate['meta.to_address']],
                                            body=self.doctemplate['content'], subject=self.doctemplate['meta.subject'],
                                            cc_address=self.cc_address, bcc_address=self.bcc_address,
                                            from_address=self.from_address,
                                            attachments=self.attachments, account=self.accont,
                                            host=self.host, port=self.port, user=self.user, password=self.password,
                                            ssl=self.ssl, tls=self.tls, html=True, async=True)
                                            
class PrintDbData(GnrBatch):
    def __init__(self, table=None, table_resource=None, class_name=None, selection=None,
                 folder=None, printParams=None, pdfParams=None, commitAfterPrint=False, **kwargs):
        #import cups
        
        super(PrintDbData, self).__init__(**kwargs)
        self.htmlMaker = self.page.site.loadTableScript(page=self.page, table=table,
                                                        respath=table_resource,
                                                        class_name=class_name)
        self.htmlMaker.parentBatch = self
        self.htmlMaker.thermoCb = self.thermoHandler
        self.table = table
        self.folder = folder or self.htmlMaker.pdfFolderPath()
        if pdfParams:
            self.printer_name = 'PDF'
            printParams = pdfParams
            self.outputFilePath = self.page.userDocument('output', 'pdf', self.docName)
        else:
            self.printer_name = printParams.pop('printer_name')
            self.outputFilePath = None
        self.thermo_maximum[1] = len(self.data)
        self.print_handler = self.page.getService('print')
        self.print_connection = self.print_handler.getPrinterConnection(self.printer_name, printParams)
        self.file_list = []
        self.commitAfterPrint = commitAfterPrint
        
    def thermoHandler(self, row=None, max_value=None, message=None):
        if max_value:
            self.thermo_reset(row, max_value=max_value)
        else:
            self.thermo_step(row=row, message=message)
            return self.stopped
            
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
            
    def thermo_chunk_message(self, chunk, row):
        if self.thermofield == '*':
            msg = self.data.dbtable.recordCaption(chunk)
        else:
            msg = chunk[self.thermofield]
        return msg
        
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
             
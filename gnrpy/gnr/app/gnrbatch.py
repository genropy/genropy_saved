#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  untitled
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#

# --------------------------- GnrWebPage subclass ---------------------------
import time
from collections import defaultdict
class GnrBatch(object):
    
    thermo_rows = 1
    
    def __init__(self, thermocb = None, thermoid=None, thermofield='*', **kwargs):
        self.thermocb = thermocb or (lambda *a,**kw:None)
        self.thermoid = thermoid
        self.thermofield = thermofield
        self.thermo_status = defaultdict(lambda: 0)
        self.thermo_message = defaultdict(lambda: '')
        self.thermo_maximum = defaultdict(lambda: None)
        self.thermo_indeterminate = defaultdict(lambda: None)
        for k,v in kwargs.items():
            if v:
                setattr(self,k,v)
    
    def data_counter(self):
        return 0
    
    def data_fetcher(self):
        for row in self.data:
            yield row
        
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
        for chunk in self.data_fetcher():
            self.process_chunk(chunk)
            self.thermo_step(chunk)
        self.post_process()
        self.thermo_end()
        return self.collect_result()
    
    def thermo_init(self, row=None):
        if self.thermoid:
            kwargs = dict()
            rows = row and [row] or range(self.thermo_rows)
            for i in rows:
                j = i+1
                kwargs['progress_%i'%j] = self.thermo_status[j]
                kwargs['message_%i'%j] = self.thermo_message[j]
                kwargs['maximum_%i'%j] = self.thermo_maximum[j]
                kwargs['indeterminate_%i'%j] = self.thermo_indeterminate[j]
            if not row:
                self.thermocb(self.thermoid, **kwargs)
            else:
                self.thermocb(self.thermoid, command='init', **kwargs)
            
    def thermo_step(self, chunk=None, step=1, row=1, status=None, message=None):
        if status is not None:
            self.thermo_status[row] = status
        else:
            self.thermo_status[row] += step
        if self.thermoid:
            kwargs = dict()
            kwargs['progress_%i'%row] = self.thermo_status[row]
            kwargs['message_%i'%row] = message or self.thermo_chunk_message(chunk=chunk, row=row)
            result = self.thermocb(self.thermoid, **kwargs)
            if result=='stop':
                self.thermocb(self.thermoid, command='stopped')
            return result
    
    def thermo_chunk_message(self, chunk, row):
        pass
        
    def thermo_end(self):
        if self.thermoid:
            self.thermocb(self.thermoid, command='end')
        

class SelectionToXls(GnrBatch):
    
    def __init__(self, selection=None, table=None, filename=None, columns=None, locale=None, **kwargs):
        super(SelectionToXls,self).__init__(**kwargs)
        self.locale = locale
        self.filename = filename or '%s.xls'%table.replace('.','_')
        self.selection = selection
        self.columns = columns
        self.tblobj = self.selection.db.table(table)
        self.data = self.selection.output('dictlist', columns=self.columns, locale=self.locale)
        self.data_len = len(self.data)
        self.thermo_maximum[0] = self.data_len
        
    def thermo_chunk_message(self, chunk, row):
        if self.thermofield=='*':
            msg = self.tblobj.recordCaption(chunk)
        else:
            msg = chunk[self.thermofield]
        return msg
        
    def data_counter(self):
        return self.data_len
    
        
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
        for c,header in enumerate(self.columns):
            self.sheet.write(0, c, header, hstyle)
        self.current_row=1
        
    def process_chunk(self, chunk):
        for c,column in enumerate(self.columns):
            if isinstance(chunk[column], list):
                value=','.join(chunk[column])
            else:
                value = chunk[column]
            self.sheet.write(self.current_row, c, value)
        self.current_row += 1
    
    def post_process(self):
        self.filePath=self.page.temporaryDocument(self.filename)
        self.fileUrl=self.page.temporaryDocumentUrl(self.filename)
        self.workbook.save(self.filePath)
        
    def collect_result(self):
        return self.fileUrl

class SelectionToPdf(GnrBatch):
    def __init__(self, table_resource=None, selection=None, table=None, folder=None, **kwargs):
        super(SelectionToPdf,self).__init__(**kwargs)
        self.pdfmaker=self.page.site.loadTableResource(page=self.page,table=table,path=table_resource)
        self.selection = selection
        self.table = table
        self.folder = folder or 'temp_print_%s'%table.replace('.','_')
        
    def data_fetcher(self):     ##### Rivedere per passare le colonne
        for row in self.selection.output('pkeylist'):
            yield row
    
    def process_chunk(self, chunk):
        self.pdfmaker.getPdfFromRecord(record=chunk,table=self.table,folder=self.folder)
        
    
class SelectedRecordsToPrint(GnrBatch):
    def __init__(self, table_resource=None, selection=None, table=None, folder=None, printParams=None, **kwargs):
        import cups
        super(SelectedRecordsToPrint,self).__init__(**kwargs)
        if table_resource:
            table_resource=self.page.site.loadTableResource(page=self.page,table=table,path=table_resource)
        self.pdfmaker=table_resource
        self.selection = selection
        self.table = table
        self.folder = folder or 'temp_print_%s'%table.replace('.','_')
        self.cups_connection = cups.Connection()
        self.printer_name = printParams['printer_name']
        printer_media=[]
        for media_option in ('paper','tray','source'):
            media_value = printParams['printer_options'] and printParams['printer_options'].pop(media_option)
            if media_value:
                printer_media.append(media_value)
        self.printer_options = printParams['printer_options'] or {}
        if printer_media:
            self.printer_options['media'] = ','.join(printer_media)
        self.pdf_list = []

    def data_fetcher(self):     ##### Rivedere per passare le colonne
        for row in self.selection.output('pkeylist'):
            yield row

    def process_chunk(self, chunk):
        outputPath= self.pdfmaker.getPdf(record=chunk,table=self.table,folder=self.folder)
        self.pdf_list.append(outputPath)
        
    def collect_result(self):
        if self.printer_name=='PDF':
            for pdf_name in self.pdf_list:
                #zip
                pass
        else:
            self.cups_connection.printFiles(self.printer_name, self.pdf_list,'GenroPrint', self.printer_options)
            


class Fake(GnrBatch):
    thermo_rows = 2
    def __init__(self, **kwargs):
        super(Fake,self).__init__(**kwargs)
        self.thermo_maximum[1] = 1000
        self.thermo_maximum[2] = 1000
        
    def data_fetcher(self):     ##### Rivedere per passare le colonne
        for row in range(1000):
            yield row

    def process_chunk(self, chunk):
        i=0
        self.thermo_step(row = 2, status = 0)
        for subrow in range(1000):
            self.thermo_step(row = 2, message = 'fake %i/%i'%(chunk,subrow))
            
    def collect_result(self):
        pass
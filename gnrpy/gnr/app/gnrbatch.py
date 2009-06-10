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
class GnrBatch(object):
    
    def __init__(self, thermocb = None, thermoid=None, thermofield='*', **kwargs):
        self.thermocb = thermocb or (lambda *a,**kw:None)
        self.thermoid = thermoid
        self.thermofield = thermofield
        self.thermostatus = 0
        for k,v in kwargs.items():
            if v:
                setattr(self,k,v)
    
    def data_counter(self):
        return 0
    
    def data_fetcher(self):
        pass
        
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
    
    def thermo_init(self):
        if self.thermoid:
            self.thermocb(self.thermoid, None, '', self.data_counter(), command='init')
            
    def thermo_step(self, chunk=None, step=1):
        self.thermostatus += step
        if self.thermoid:
            msg = self.thermo_chunk_message(chunk=chunk)
            result = self.thermocb(self.thermoid, self.thermostatus, msg)
            if result=='stop':
                self.thermocb(self.thermoid, command='stopped')
            return result
        
    def thermo_chunk_message(self, chunk):
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
    
    def thermo_chunk_message(self, chunk):
        if self.thermofield=='*':
            msg = self.tblobj.recordCaption(chunk)
        else:
            msg = chunk[self.thermofield]
        
    
    def data_fetcher(self):
        for row in self.selection.output('dictlist', columns=self.columns, locale=self.locale):
            yield row
        
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
            self.sheet.write(self.current_row, c, chunk[column])
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
        if table_resource:
            table_resource=self.page.site.loadTableResource(page=self.page,table=table,path=table_resource)
        self.pdfmaker=table_resource
        self.selection = selection
        self.table = table
        self.folder = folder or 'temp_print_%s'%table.replace('.','_')
        
    def data_fetcher(self):     ##### Rivedere per passare le colonne
        for row in self.selection.output('pkeylist'):
            yield row
    
    def process_chunk(self, chunk):
        self.pdfmaker.getPdf(self.table,chunk,folder=self.folder)
        self.pdfmaker.toPdf(self.pdfmaker.filePath)
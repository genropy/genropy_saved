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
    def __init__(self,data=None,runKwargs=None, thermocb = None, thermoid=None,thermofield='*',**kwargs):
        self.thermocb = thermocb or (lambda *a,**kw:None)
        self.thermoid = thermoid
        self.thermofield = thermofield
        self.thermo_status = defaultdict(lambda: 0)
        self.thermo_message = defaultdict(lambda: '')
        self.thermo_maximum = defaultdict(lambda: None)
        self.thermo_indeterminate = defaultdict(lambda: None)
        self.runKwargs = runKwargs.asDict(True) if runKwargs else {}
        self.data = data
        for k,v in kwargs.items():
            if v:
                setattr(self,k,v)
    
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
        self.thermo_end()
        return self.collect_result()
        
    def process(self):
        print 'in process'
        for chunk in self.data_fetcher():
            print 'calling process_chunk'
            self.process_chunk(chunk,**self.runKwargs)
            #self.thermo_step(chunk)
    
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
        print 'thermo_end'
        if self.thermoid:
            print 'thermo_end 2'
            self.thermocb(self.thermoid, command='end')
        
class SelectionToXls(GnrBatch):
    def __init__(self, data=None, table=None, filename=None, columns=None, locale=None, **kwargs):
        if columns:
            columns = columns.split(',')
        else:
            columns = data.columns
        self.columns = columns
        self.locale = locale
        self.filename = filename or '%s.xls'%table.replace('.','_')
        data=data.output('dictlist', columns=self.columns, locale=self.locale)
        super(SelectionToXls,self).__init__(data=data,**kwargs)
        self.tblobj = self.page.db.table(table)
        self.thermo_maximum[0] = self.data_counter()
        
    def thermo_chunk_message(self, chunk, row):
        if self.thermofield=='*':
            msg = self.tblobj.recordCaption(chunk)
        else:
            msg = chunk[self.thermofield]
        return msg

    
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
        self.table = table
        self.folder = folder or 'temp_print_%s'%table.replace('.','_')
        
    def data_fetcher(self):     ##### Rivedere per passare le colonne
        for row in self.data.output('pkeylist'):
            yield row
    
    def process_chunk(self, chunk):
        self.pdfmaker.getPdfFromRecord(record=chunk,table=self.table,folder=self.folder)
        
class PrintDbData(GnrBatch):
    def __init__(self, table=None,table_resource=None, class_name=None, selection=None,
                folder=None, printParams=None, pdfParams=None,**kwargs):
        import cups
        super(PrintDbData,self).__init__(**kwargs)
        self.htmlMaker = self.page.site.loadTableScript(page=self.page,table=table,
                                                      respath=table_resource,
                                                      class_name=class_name)
        self.htmlMaker.parentBatch = self
        self.table = table
        self.folder = folder or self.htmlMaker.pdfFolderPath()
        if pdfParams:
            self.printer_name = 'PDF'
            printParams = pdfParams
            self.outputFilePath = self.page.temporaryDocument(self.docName)
        else:  
            self.printer_name = printParams.pop('printer_name')
            self.outputFilePath = None
        self.print_connection = self.page.site.print_handler.getPrinterConnection(self.printer_name, printParams)
        self.file_list = []
        
    def collect_result(self):
        result = self.print_connection.printFiles(self.file_list, 'GenroPrint', 
                    storeFolder=self.folder, outputFilePath=self.outputFilePath)
        if result:
            return self.page.temporaryDocumentUrl(result)
                     
    def process_chunk(self, chunk, **kwargs):
        self.htmlMaker(chunk, rebuild=self.rebuild,**kwargs)
        self.file_list.append(self.htmlMaker.filepath)
    
    def data_fetcher(self):     ##### Rivedere per passare le colonne
        for row in self.data.output('pkeylist'):
            yield row

class PrintSelection(PrintDbData):
    pass


class PrintRecord(PrintDbData):
    def process(self):
        self.process_chunk(self.data,**self.runKwargs)

################################
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
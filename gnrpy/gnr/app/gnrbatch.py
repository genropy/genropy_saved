#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  untitled
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#

from time import time
from collections import defaultdict

class GnrBatch(object):
    thermo_rows = 1
    def __init__(self,data=None,runKwargs=None, thermocb = None, thermoId=None,thermofield='*',thermodelay=0.5,**kwargs):
        self.thermocb = thermocb or (lambda *a,**kw:None)
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
        result = self.collect_result()
        self.thermo_end()
        return result

        
    def process(self):
        for chunk in self.data_fetcher():
            self.thermo_step(chunk)
            if self.stopped:
                break
            self.process_chunk(chunk,**self.runKwargs)
            
    def thermo_init(self, row=None):
        if self.thermoId:
            kwargs = dict()
            rows = row and [row] or range(self.thermo_rows)
            print rows
            for i in rows:
                j = i+1
                kwargs['progress_%i'%j] = self.thermo_status[j]
                kwargs['message_%i'%j] = self.thermo_message[j]
                kwargs['maximum_%i'%j] = self.thermo_maximum[j]
                kwargs['indeterminate_%i'%j] = self.thermo_indeterminate[j]
            if not row:
                self.thermocb(self.thermoId, **kwargs)
            else:
                self.thermocb(self.thermoId, command='init', **kwargs)
            
    def thermo_reset(self,row,max_value):
        kwargs = dict()
        self.thermo_maximum[row] = max_value
        kwargs['maximum_%i'%row] = max_value
        self.thermo_status[row] = 0
        kwargs['progress_%i'%row] = self.thermo_status[row]
        self.last_thermotime=time()
        return self.thermocb(self.thermoId, **kwargs)
        
    def thermo_step(self, chunk=None, row=1, status=None, message=None,step=1):
        kwargs = dict()
        if status is not None:
            self.thermo_status[row] = status
        else:
            self.thermo_status[row] += step
        if self.thermoId:
            if time()-self.last_thermotime >= self.thermodelay:
                self.last_thermotime=time()
                kwargs['progress_%i'%row] = self.thermo_status[row]
                kwargs['message_%i'%row] = message or self.thermo_chunk_message(chunk=chunk, row=row)
                result = self.thermocb(self.thermoId, **kwargs)
                if result=='stop':
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
        else:
            columns = data.columns
        self.colHeaders={}
        if('structure') in kwargs:
            self.colHeaders=dict([(x.replace('.','_').replace('@','_').replace('$',''),y) for x,y in kwargs['structure']['#0.#0'].digest('#a.field,#a.name')])
            columns=[c for c in columns if c in self.colHeaders ]
        self.columns = columns
        self.locale = locale
        self.filename = filename or '%s.xls'%table.replace('.','_')
        self.colAttrs=data.colAttrs
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
            self.sheet.write(0, c, self.colHeaders[header], hstyle)
        self.current_row=1
        
    def process_chunk(self, chunk):
        for c,column in enumerate(self.columns):
            if isinstance(chunk[column], list):
                value=','.join([str(x != None and x or '') for x in chunk[column]])
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

        
class PrintDbData(GnrBatch):
    def __init__(self, table=None,table_resource=None, class_name=None, selection=None,
                folder=None, printParams=None, pdfParams=None, commitAfterPrint=False, **kwargs):
        #import cups
        
        super(PrintDbData,self).__init__(**kwargs)
        self.htmlMaker = self.page.site.loadTableScript(page=self.page,table=table,
                                                      respath=table_resource,
                                                      class_name=class_name)
        self.htmlMaker.parentBatch = self
        self.htmlMaker.thermoCb = self.thermoHandler
        self.table = table
        self.folder = folder or self.htmlMaker.pdfFolderPath()
        if pdfParams:
            self.printer_name = 'PDF'
            printParams = pdfParams
            self.outputFilePath = self.page.temporaryDocument(self.docName)
        else:  
            self.printer_name = printParams.pop('printer_name')
            self.outputFilePath = None
        self.thermo_maximum[1] = len(self.data)
        self.print_handler = self.page.site.print_handler
        self.print_connection = self.print_handler.getPrinterConnection(self.printer_name, printParams)
        self.file_list = []
        self.commitAfterPrint=commitAfterPrint
        
    def thermoHandler(self,row=None,max_value=None,message=None):
        if max_value:
            self.thermo_reset(row,max_value=max_value)
        else:
            self.thermo_step(row=row,message=message)
            return self.stopped
        
        
    def collect_result(self):
        result = None
        if self.file_list:        
            result = self.print_connection.printFiles(self.file_list, 'GenroPrint', outputFilePath=self.outputFilePath)
        if result:
            return self.page.temporaryDocumentUrl(result)
                     
    def process_chunk(self, chunk, **kwargs):
        html = self.htmlMaker(chunk['pkey'], rebuild=self.rebuild,**kwargs)
        if html!=False:
            self.file_list.append(self.print_handler.htmlToPdf(self.htmlMaker.filepath,self.folder))

    def thermo_chunk_message(self, chunk, row):
        if self.thermofield=='*':
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
        self.process_chunk(dict(pkey=self.data),**self.runKwargs)

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
##################################

class ProgressThermo(object):
    def __init__(self, name,lines=None,**kwargs):
        
        self.name = name
        self.lines = lines
        self.lines.update(dict([(k[8:],dict(maximum=v)) for k,v in kwargs.items() if k.startswith('maximum_')]))

    def setLine(self,line,**kwargs):
        self.lines[line].update(kwargs)
        
        
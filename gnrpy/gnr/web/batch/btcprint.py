#!/usr/bin/env python
# encoding: utf-8
"""
print.py

Created by Francesco Porcari on 2010-10-16.
Copyright (c) 2010 Softwell. All rights reserved.
"""
import os
import tempfile

from gnr.web.batch.btcbase import BaseResourceBatch

class BaseResourcePrint(BaseResourceBatch):
    def __init__(self,*args,**kwargs):
        super(BaseResourcePrint,self).__init__(**kwargs)
        self.htmlMaker = self.page.site.loadTableScript(page=self.page,table=self.maintable ,
                                                        respath=self.html_res,class_name='Main')
                                    
        
    
    def _pre_process(self):
        self.batch_options = self.batch_parameters['batch_options']
        self.print_mode = self.batch_options['print_mode']
        self.print_options = self.batch_options['print_mode_option']
        self.print_handler = self.page.getService('print')             #porting stuff
        self.folder = self.htmlMaker.pdfFolderPath()         #porting stuff
        if self.print_mode=='pdf':
            filename= self.print_options['save_as'] or self.batch_prefix
            self.print_connection = self.print_handler.getPrinterConnection('PDF', self.print_options)
            self.output_file_path = self.page.userDocument('output','pdf',filename)
    
    def result_handler(self):
        resultAttr = dict()
        if self.print_mode=='direct':
            print x
        elif self.print_mode=='pdf':
            filename = self.print_connection.printFiles(self.file_list, 'GenroPrint', outputFilePath=self.output_file_path)
            if filename:
                resultAttr['url'] = self.page.userDocumentUrl('output','pdf',filename)
        return 'Execution completed',resultAttr
    
    def table_script_option_pane(self,pane):
        bc = pane.borderContainer()
        top = bc.contentPane(region='top')
        fb = top.formbuilder(cols=1, border_spacing='3px',action='SET .print_mode=$1.print_mode',group='print_mode')
        fb.radiobutton(value='^.direct',default_value=True,label='Direct print',print_mode='direct')
        fb.radiobutton(value='^.pdf',label='Download Pdf',print_mode='pdf')
        fb.radiobutton(value='^.mail',label='Send as mail',print_mode='mail')
        fb.radiobutton(value='^.server',label='Send to printer',print_mode='server')

        center = bc.stackContainer(region='center',selectedPage='^.#parent.print_mode',
                                    margin='3px',border='2px solid white',datapath='.print_mode_option')
        center.contentPane(pageName='direct')
        self.table_script_pdf_options(center.contentPane(pageName='pdf'))
        center.contentPane(pageName='mail',datapath='mail')
        serverprint = center.contentPane(pageName='server')
        serverprint.button('Options',action='FIR #printer_option_dialog.open=resource_name',
                    resource_name='=.#parent.batch.resource_name')
    
    def _old_in_batch(self, table=None,table_resource=None, class_name=None, selection=None,
                folder=None, printParams=None, pdfParams=None, commitAfterPrint=False,batch_note=None, **kwargs):
        
        self.htmlMaker = self.page.site.loadTableScript(page=self.page,table=table,
                                                      respath=table_resource,
                                                      class_name=class_name)
        self.htmlMaker.parentBatch = self
        self.table = table
        self.folder = folder or self.htmlMaker.pdfFolderPath()
        if pdfParams:
            self.printer_name = 'PDF'
            printParams = pdfParams
            self.outputFilePath = self.page.userDocument('output','pdf',self.docName)
        else:  
            self.printer_name = printParams.pop('printer_name')
            self.outputFilePath = None
        self.print_handler = self.page.getService('print')
        self.print_connection = self.print_handler.getPrinterConnection(self.printer_name, printParams)
        self.file_list = []
        self.commitAfterPrint=commitAfterPrint
        self.batch_note = batch_note
    
    def _old_in_tablescrip(self):
        #if not (dontSave or pdf):
        #self.filepath=filepath or os.path.join(self.hmtlFolderPath(),self.outputDocName(ext='html'))
        #else:
        #    self.filepath = None
        #if rebuild or not os.path.isfile(self.filepath):
        #    html=self.createHtml(filepath=self.filepath , **kwargs)
            
        #else:
        #    with open(self.filepath,'r') as f:
        #        html=f.read()
        if pdf:
            temp = tempfile.NamedTemporaryFile(suffix='.pdf')
            self.page.getService('print').htmlToPdf(self.filepath, temp.name)
            with open(temp.name,'rb') as f:
                html=f.read()
        self.onRecordExit(self.getData('record'))
        return html
        
        def pdfFolderPath(self):
            return self.getFolderPath(*self.pdf_folder.split('/'))
    
    
    def table_script_pdf_options(self,pane):
        fb = pane.formbuilder(cols=1)
        fb.dataFormula('.zipped','false',_onStart=True)
        fb.textbox(value='^.save_as',lbl='!!Save as')
        fb.checkbox(value='^.zipped',label='!!Zip folder')
#!/usr/bin/env python
# encoding: utf-8
"""
print.py

Created by Francesco Porcari on 2010-10-16.
Copyright (c) 2010 Softwell. All rights reserved.
"""
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
        self.print_handler = self.page.getService('print')           

    
    def result_handler(self):
        resultAttr = dict()
        if self.print_mode=='direct':
            print x
        else:
            printer_name = 'PDF' if self.print_mode=='pdf' else self.print_options.pop('printer_name')
            pdfprinter = self.print_handler.getPrinterConnection(printer_name, self.print_options)
            filename = pdfprinter.printFiles(self.results.values(), 'GenroPrint', 
                                             outputFilePath=self.page.site.getStaticPath('user:output','pdf',
                                             self.print_options['save_as'] or self.batch_prefix))
            if filename:
                resultAttr['url'] = self.page.site.getStaticUrl('user:output','pdf',filename)

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
        self.table_script_mail_options(center.contentPane(pageName='mail',datapath='mail'))
        self.table_script_server_print_options(center.contentPane(pageName='server'))
        
    def table_script_server_print_options(self,pane):
        pane.button('Options',action='FIR #printer_option_dialog.open=resource_name',
                    resource_name='=.#parent.batch.resource_name')
        
    def table_script_mail_options(self,pane):
        pass

    def table_script_pdf_options(self,pane):
        fb = pane.formbuilder(cols=1)
        fb.dataFormula('.zipped','false',_onStart=True)
        fb.textbox(value='^.save_as',lbl='!!Save as')
        fb.checkbox(value='^.zipped',label='!!Zip folder')
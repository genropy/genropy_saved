#!/usr/bin/env python
# encoding: utf-8
"""
print.py

Created by Francesco Porcari on 2010-10-16.
Copyright (c) 2010 Softwell. All rights reserved.
"""
from gnr.web.batch.btcbase import BaseResourceBatch
from gnr.core.gnrbag import Bag
class BaseResourcePrint(BaseResourceBatch):
    dialog_height = '300px'
    dialog_width = '460px'
    dialog_height_no_par = '200px'
        
    def __init__(self,*args,**kwargs):
        super(BaseResourcePrint,self).__init__(**kwargs)
        self.mail_preference = self.page.getUserPreference('mail',pkg='adm') or Bag(self.page.application.config.getNode('mail').attr)
        self.htmlMaker = self.page.site.loadTableScript(page=self.page,table=self.maintable ,
                                                        respath=self.html_res,class_name='Main')
                                        
    def _pre_process(self):
        self.batch_options = self.batch_parameters['batch_options']
        self.print_mode = self.batch_options['print_mode']
        self.server_print_options = self.batch_parameters['_printerOptions']
        self.print_options = self.batch_options['print_mode_option']
        self.print_handler = self.page.getService('print')           
    
    def print_selection(self,thermo_selection=None,thermo_record=None):
        thermo_s = dict(line_code='selection',message='get_record_caption')
        thermo_s.update(thermo_selection or {})
        thermo_r = dict(line_code='record')
        thermo_r.update(thermo_record or {})
        if not 'templates' in self.batch_parameters:
            self.batch_parameters['templates'] = self.templates
        pkeys = self.get_selection_pkeys()
        pdf = self.print_mode=='pdf' or self.print_mode == 'mail_pdf' or self.print_mode == 'mail_deliver'
        for pkey in self.btc.thermo_wrapper(pkeys,**thermo_s):
            result = self.htmlMaker(record=pkey,thermo=thermo_r,pdf=pdf,
                                    **self.batch_parameters)
            
            self.storeResult(pkey,result,self.htmlMaker.record)           
    
    def do(self):
        self.print_selection()

    def result_handler(self):
        resultAttr = dict()
        result = getattr(self,'result_handler_%s' %self.print_mode)(resultAttr)
        result = result or 'Execution completed'
        return result, resultAttr
    
    def result_handler_mail_deliver(self,resultAttr):
        mailmanager = self.page.getService('mail')
        mailpars = dict()
        mailpars.update(self.mail_preference.asDict(True))
        mailpars.update(self.print_options.getItem('mail').asDict(True))
        
        for pkey,result in self.results.items():
            record = self.records[pkey]
            mailpars['attachments'] = [result]
            mailpars['to_address'] = record[self.mail_address]
            mailmanager.sendmail(**mailpars)

    def result_handler_mail_pdf(self,resultAttr):
        mailmanager = self.page.getService('mail')
        mailpars = dict()
        mailpars.update(self.mail_preference.asDict(True))
        mailpars.update(self.print_options.getItem('mail').asDict(True))
        mailpars['attachments'] = self.results.values()
        mailmanager.sendmail(**mailpars)
    
    def result_handler_client_print(self,resultAttr):
        print 'client print:todo'
        
    def result_handler_server_print(self,resultAttr):
        printer = self.print_handler.getPrinterConnection(self.server_print_options['printer_name'],**self.server_print_options)
        return printer.printCups(self.results.values(), self.batch_title )

        
    def result_handler_pdf(self,resultAttr):
        pdfprinter = self.print_handler.getPrinterConnection('PDF', self.print_options)
        save_as = self.print_options['save_as'] or self.batch_title
        filename = pdfprinter.printPdf(self.results.values(), self.batch_title, 
                                      outputFilePath=self.page.site.getStaticPath('user:output','pdf',save_as,autocreate=True))
        if filename:
            resultAttr['url'] = self.page.site.getStaticUrl('user:output','pdf',filename)
    
    def table_script_option_pane(self,pane):
        bc = pane.borderContainer()
        top = bc.contentPane(region='top',padding='6px').div(_class='ts_printMode',padding='2px')
        fb = top.formbuilder(cols=5, border_spacing='4px',margin_top='2px',font_size='.9em',
                            action='SET .print_mode=$1.print_mode',group='print_mode',lbl_width='3em')
        fb.data('.print_mode','client_print')
        fb.radiobutton(value='^.client_print',default_value=True,label='!!Client print',print_mode='client_print')
        fb.radiobutton(value='^.server_print',label='!!Server print',print_mode='server_print')
        fb.radiobutton(value='^.pdf',label='!!Pdf download',print_mode='pdf')
        fb.radiobutton(value='^.mail_pdf',label='!!Pdf by mail',print_mode='mail_pdf')
        fb.radiobutton(value='^.mail_deliver',label='!!Deliver mails',print_mode='mail_deliver')
        
        center = bc.stackContainer(region='center',selectedPage='^.#parent.print_mode',
                                    margin='3px',datapath='.print_mode_option')
                                    
        self.table_script_options_client_print(center.contentPane(pageName='client_print'))
        self.server_print_option_pane(center.contentPane(pageName='server_print'))
        self.table_script_options_pdf(center.contentPane(pageName='pdf'))
        self.table_script_options_mail_pdf(center.contentPane(pageName='mail_pdf',datapath='.mail'))
        self.table_script_options_mail_deliver(center.contentPane(pageName='mail_deliver',datapath='.mail'))
        
    def table_script_options_client_print(self,pane):
        pane.div()
        
    #def table_script_options_server_print(self,pane):
    #    pane.button('Options',action='FIR #printer_option_dialog.open=resource_name',
    #                resource_name='=.#parent.batch.resource_name')
    #
    def table_script_options_pdf(self,pane):
        fb = self.table_script_fboptions(pane,fld_width=None,tdl_width='6em')
        fb.data('.zipped',False)
        fb.textbox(value='^.save_as',lbl='!!Document name',width='100%')
        fb.checkbox(value='^.zipped',label='!!Zip folder')
        
    def table_script_options_mail_pdf(self,pane):
        fb = self.table_script_fboptions(pane)
        fb.textbox(value='^.to_address',lbl='!!To')
        fb.textbox(value='^.cc_address',lbl='!!CC')
        fb.textbox(value='^.subject',lbl='!!Subject')
        fb.simpleTextArea(value='^.body',lbl='!!Body',height='10ex',lbl_vertical_align='top')
    
    def table_script_options_mail_deliver(self,pane):
        fb = self.table_script_fboptions(pane)
        fb.textbox(value='^.cc_address',lbl='!!CC',width='100%')
        fb.textbox(value='^.subject',lbl='!!Subject',width='100%')
        fb.simpleTextArea(value='^.body',lbl='!!Body',height='14ex',lbl_vertical_align='top')
    
    def table_script_fboptions(self,pane,fld_width='100%',tdl_width='4em'):
        return pane.div(margin_right='5px').formbuilder(cols=1,width='100%',tdl_width=tdl_width,
                             border_spacing='4px',fld_width=fld_width)




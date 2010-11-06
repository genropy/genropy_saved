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
    dialog_height_no_par = '225px'
    templates = '' #CONTROLLARE
        
    def __init__(self,*args,**kwargs):
        super(BaseResourcePrint,self).__init__(**kwargs)
        self.mail_preference = self.page.getUserPreference('mail',pkg='adm') or self.page.getPreference('mail',pkg='adm') or Bag(self.page.application.config.getNode('mail').attr)
        self.htmlMaker = self.page.site.loadTableScript(page=self.page,table=self.maintable ,
                                                        respath=self.html_res,class_name='Main')
                                        
    def _pre_process(self):
        self.batch_options = self.batch_parameters['batch_options']
        self.print_mode = self.batch_options['print_mode']
        self.server_print_options = self.batch_parameters['_printerOptions']
        self.print_options = self.batch_options['print_mode_option']
        self.print_handler = self.page.getService('print')     
        self.pdf_make = self.print_mode not in ('server_print','client_print')      
    
    def print_selection(self,thermo_selection=None,thermo_record=None):
        thermo_s = dict(line_code='selection',message='get_record_caption',tblobj=self.tblobj)
        thermo_s.update(thermo_selection or {})
        thermo_r = dict(line_code='record',message='get_record_caption')
        thermo_r.update(thermo_record or {})
        if isinstance(thermo_s['message'],basestring) and hasattr(self,thermo_s['message']):
            thermo_s['message'] = getattr(self,thermo_s['message'])
        if isinstance(thermo_r['message'],basestring) and hasattr(self.htmlMaker,thermo_r['message']):
            thermo_r['message'] = getattr(self.htmlMaker,thermo_r['message'])
        if not 'templates' in self.batch_parameters:
            self.batch_parameters['templates'] = self.templates  #CONTROLLARE
        records = self.get_records()
        pkeyfield = self.tblobj.pkey
        
        for record in self.btc.thermo_wrapper(records,maximum=len(self.get_selection()),**thermo_s):
            self.print_record(record=record,thermo=thermo_r,storagekey=record[pkeyfield])
    
    def print_record(self,record=None,thermo=None,storagekey=None):
        result = self.htmlMaker(record=record,thermo=thermo,pdf=self.pdf_make,
                                **self.batch_parameters)
        self.onRecordExit(record)
        if result:
            self.storeResult(storagekey,result,record,filepath=self.htmlMaker.filepath)

    def onRecordExit(self,record=None):
        "override"
        pass
    
    def do(self):
        self.print_selection()
                 
    def get_record_caption(self,item,progress,maximum,**kwargs):
        caption = '%s (%i/%i)' % (self.tblobj.recordCaption(item),
                              progress,maximum)
        return caption
        
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
        pass
        #self.page.setInClientData(path='#table_script_dlg_parameters.close',value=True,fired=True)
        #
        #for html in self.result_info.values():
        #    self.page.setInClientData(path='gnr.printurl',value=html,fired=True)

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
        bc = pane.borderContainer(height='200px')
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
        fb = self.table_script_fboptions(pane,tdl_width='3em')
        fb.simpleTextArea(value='^.#parent.#parent.batch_note',
                        height='20ex',lbl='!!Notes',
                        lbl_vertical_align='top')
        
    def table_script_options_pdf(self,pane):
        fb = self.table_script_fboptions(pane,fld_width=None,tdl_width='10em')
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
    
    def table_script_fboptions(self,pane,fld_width='100%',tdl_width='4em',**kwargs):
        return pane.div(margin_right='5px').formbuilder(cols=1,width='100%',tdl_width=tdl_width,
                             border_spacing='4px',fld_width=fld_width)




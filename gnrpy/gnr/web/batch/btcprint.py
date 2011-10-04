#!/usr/bin/env python
# encoding: utf-8
#
#btcprint.py
#
#Created by Francesco Porcari on 2010-10-16.
#Copyright (c) 2011 Softwell. All rights reserved.

from gnr.web.batch.btcbase import BaseResourceBatch
from gnr.core.gnrstring import slugify
from gnr.core.gnrbag import Bag

class BaseResourcePrint(BaseResourceBatch):
    """Base resource to make a :ref:`print`"""
    batch_immediate = False
    dialog_height = '300px'
    dialog_width = '460px'
    dialog_height_no_par = '245px'
    html_res = ''
    mail_address = ''
    mail_tags = 'admin'
    templates = '' #CONTROLLARE
    
    def __init__(self, *args, **kwargs):
        super(BaseResourcePrint, self).__init__(**kwargs)
        self.mail_preference = self.page.getUserPreference('mail', pkg='adm') or self.page.getPreference('mail',
                                                                                                         pkg='adm') or Bag(
                self.page.application.config.getNode('mail').attr)
        self.htmlMaker = self.page.site.loadTableScript(page=self.page, table=self.maintable,
                                                        respath=self.html_res, class_name='Main')
        if not hasattr(self, 'mail_tags'):
            self.mail_tags = 'mail'

    def _pre_process(self):
        self.pre_process()
        self.batch_options = self.batch_parameters['batch_options']
        self.print_mode = self.batch_options['print_mode']
        self.server_print_options = self.batch_parameters['_printerOptions']
        self.print_options = self.batch_options['print_mode_option']
        self.print_handler = self.page.getService('print')
        self.pdf_make = self.print_mode != 'client_print'

    def print_selection(self, thermo_selection=None, thermo_record=None):
        """add???
        
        :param thermo_selection: add???
        :param thermo_record: add???"""
        thermo_s = dict(line_code='selection', message='get_record_caption', tblobj=self.tblobj)
        thermo_s.update(thermo_selection or {})
        thermo_r = dict(line_code='record', message='get_record_caption')
        thermo_r.update(thermo_record or {})
        if isinstance(thermo_s['message'], basestring) and hasattr(self, thermo_s['message']):
            thermo_s['message'] = getattr(self, thermo_s['message'])
        if isinstance(thermo_r['message'], basestring) and hasattr(self.htmlMaker, thermo_r['message']):
            thermo_r['message'] = getattr(self.htmlMaker, thermo_r['message'])
        if not 'templates' in self.batch_parameters:
            self.batch_parameters['templates'] = self.templates  #CONTROLLARE
        records = self.get_records()
        pkeyfield = self.tblobj.pkey
        for record in self.btc.thermo_wrapper(records, maximum=len(self.get_selection()), **thermo_s):
            self.print_record(record=record, thermo=thermo_r, storagekey=record[pkeyfield])

    def print_record(self, record=None, thermo=None, storagekey=None):
        """add???
        
        :param record: add???
        :param thermo: add???
        :param storagekey: add???"""
        result = self.htmlMaker(record=record, thermo=thermo, pdf=self.pdf_make,
                                **self.batch_parameters)
        self.onRecordExit(record)
        if result:
            self.storeResult(storagekey, result, record, filepath=self.htmlMaker.filepath)
            
    def onRecordExit(self, record=None):
        """Hook method.
        
        :param record: the result records of the executed batch"""
        pass
        
    def do(self):
        """add???"""
        self.print_selection()
        
    def get_record_caption(self, item, progress, maximum, **kwargs):
        """add???
        
        :param item: add???
        :param progress: add???
        :param maximum: add???"""
        caption = '%s (%i/%i)' % (self.tblobj.recordCaption(item),
                                  progress, maximum)
        return caption
        
    def result_handler(self):
        """add???"""
        resultAttr = dict()
        result = getattr(self, 'result_handler_%s' % self.print_mode)(resultAttr)
        result = result or ''
        return result, resultAttr
        
    def result_handler_mail_deliver(self, resultAttr):
        """add???
        
        :param resultAttr: add???"""
        mailmanager = self.page.getService('mail')
        mailpars = dict()
        mailpars.update(self.mail_preference.asDict(True))
        mailpars.update(self.print_options.getItem('mail').asDict(True))

        for pkey, result in self.results.items():
            record = self.records[pkey]
            mailpars['attachments'] = [result]
            mailpars['to_address'] = record[self.mail_address]
            mailmanager.sendmail(**mailpars)

    def result_handler_mail_pdf(self, resultAttr):
        """add???
        
        :param resultAttr: add???"""
        mailmanager = self.page.getService('mail')
        mailpars = dict()
        mailpars.update(self.mail_preference.asDict(True))
        mailpars.update(self.print_options.getItem('mail').asDict(True))
        mailpars['attachments'] = self.results.values()
        mailmanager.sendmail(**mailpars)
        
    def result_handler_server_print(self, resultAttr):
        """add???
        
        :param resultAttr: add???"""
        printer = self.print_handler.getPrinterConnection(self.server_print_options.pop('printer_name'),
                                                          **self.server_print_options.asDict(True))
        return printer.printCups(self.results.values(), self.batch_title)


    def result_handler_pdf(self, resultAttr):
        """add???
        
        :param resultAttr: add???"""
        pdfprinter = self.print_handler.getPrinterConnection('PDF', self.print_options)
        save_as = slugify(self.print_options['save_as'] or self.batch_title)
        filename = pdfprinter.printPdf(self.results.values(), self.batch_title,
                                       outputFilePath=self.page.site.getStaticPath('user:output', 'pdf', save_as,
                                                                                   autocreate=-1))
        if filename:
            self.fileurl = self.page.site.getStaticUrl('user:output', 'pdf', filename, nocache=True, download=True)
            resultAttr['url'] = self.fileurl
            resultAttr['document_name'] = save_as
            resultAttr['url_print'] = self.page.site.getStaticUrl('user:output', 'pdf', filename, nocache=True,target='_blank')
            if self.batch_immediate=='print':
                self.page.setInClientData(path='gnr.clientprint',value=self.page.site.getStaticUrl('user:output', 'pdf', filename, nocache=True),fired=True)
            elif self.batch_immediate=='download':
                self.page.setInClientData(path='gnr.downloadurl',value=self.page.site.getStaticUrl('user:output', 'pdf', filename, nocache=True),fired=True)
                
    def table_script_option_pane(self, pane, resource=None):
        """Define the *print region* of the :ref:`print_setting_dialog`
        
        :param pane: a :ref:`contentpane` that works as the :ref:`layout widget <layout>`
                     father of the method
        :param resource: used to complete the :ref:`datapath` of the method that handle the
                         server prints. In particular, the datapath syntax is
                         ``gnr.server_print.printers`` followed by the string included in
                         the *resource* attribute"""
        bc = pane.borderContainer(height='220px')
        top = bc.contentPane(region='top', padding='6px').div(_class='ts_printMode', padding='2px')
        bottom = bc.borderContainer(region='bottom', height='60px')
        bottom.contentPane(region='top').div('Notes', _class='bgcolor_darkest', color='white', padding_left='2px')
        bottom.contentPane(region='center', overflow='hidden', margin='4px').simpleTextArea(
                value='^.#parent.batch_note')
        fb = top.formbuilder(cols=4, border_spacing='4px', margin_top='2px', font_size='.9em',
                             action='SET .print_mode=$1.print_mode', field_group='print_mode', lbl_width='1.5em')
        fb.data('.print_mode', 'pdf')
        #fb.radiobutton(value='^.client_print',default_value=True,label='!!Client print',print_mode='client_print')
        fb.radiobutton(value='^.pdf', label='!!PDF', lbl=' ', print_mode='pdf', default_value=True)
        fb.radiobutton(value='^.server_print', label='!!Server print', lbl=' ', print_mode='server_print')

        center = bc.stackContainer(region='center', selectedPage='^.#parent.print_mode', datapath='.print_mode_option')

        self.table_script_options_pdf(center.contentPane(pageName='pdf'))
        self.server_print_option_pane(center.contentPane(pageName='server_print'), resource=resource)
        if self.current_batch.mail_tags and self.application.checkResourcePermission(self.current_batch.mail_tags,
                                                                                     self.userTags):
            fb.radiobutton(value='^.mail_pdf', label='!!PDF by mail', print_mode='mail_pdf', lbl=' ')
            self.table_script_options_mail_pdf(center.contentPane(pageName='mail_pdf', datapath='.mail'))
            if hasattr(self.current_batch, 'mail_address'):
                fb.radiobutton(value='^.mail_deliver', label='!!Deliver mails', print_mode='mail_deliver', lbl=' ')
                self.table_script_options_mail_deliver(center.contentPane(pageName='mail_deliver', datapath='.mail'))

    def table_script_options_pdf(self, pane):
        """Define the "File Name" textbox and the "Zip folder" checkbox in the
        :ref:`print_setting_dialog_print` of the :ref:`print_setting_dialog`
        
        :param pane: the :ref:`contentpane` received by the method"""
        fb = self.table_script_fboptions(pane, fld_width=None, tdl_width='5em')
        fb.data('.zipped', False)
        fb.textbox(value='^.save_as', lbl='!!File Name', width='100%')
        fb.checkbox(value='^.zipped', label='!!Zip folder')

    def table_script_options_mail_pdf(self, pane):
        """Define the mail fields of the :ref:`print_pdf_by_mail` pane of the
        :ref:`print_setting_dialog_print` of the :ref:`print_setting_dialog`
        
        :param pane: the :ref:`contentpane` received by the method"""
        fb = self.table_script_fboptions(pane)
        fb.textbox(value='^.to_address', lbl='!!To')
        fb.textbox(value='^.cc_address', lbl='!!CC')
        fb.textbox(value='^.subject', lbl='!!Subject')
        fb.simpleTextArea(value='^.body', lbl='!!Body', height='5ex', lbl_vertical_align='top')
        
    def table_script_options_mail_deliver(self, pane):
        """Define the mail fields of the :ref:`print_deliver_mails` pane of the
        :ref:`print_setting_dialog_print` of the :ref:`print_setting_dialog`
        
        :param pane: the :ref:`contentpane` received by the method"""
        fb = self.table_script_fboptions(pane)
        fb.textbox(value='^.cc_address', lbl='!!CC', width='100%')
        fb.textbox(value='^.subject', lbl='!!Subject', width='100%')
        fb.simpleTextArea(value='^.body', lbl='!!Body', height='8ex', lbl_vertical_align='top')

    def table_script_fboptions(self, pane, fld_width='100%', tdl_width='4em', **kwargs):
        """The :ref:`formbuilder` with default styles for the following methods:
        
        * :meth:`table_script_options_pdf`
        * :meth:`table_script_options_mail_pdf`
        * :meth:`table_script_options_mail_deliver`
        
        :param pane: the :ref:`contentpane` received by the method
        :param fld_width: a :ref:`formbuilder attribute <formbuilder_prefixes>`
        :param tdl_width: a :ref:`formbuilder attribute <formbuilder_prefixes>`"""
        return pane.div(margin_right='5px').formbuilder(cols=1, width='100%', tdl_width=tdl_width,
                                                        border_spacing='4px', fld_width=fld_width)
                                                        
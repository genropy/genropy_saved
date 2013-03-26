#!/usr/bin/env python
# encoding: utf-8
#
#btcprint.py
#
#Created by Francesco Porcari on 2010-10-16.
#Copyright (c) 2011 Softwell. All rights reserved.

from gnr.web.batch.btcbase import BaseResourceBatch
from gnr.core.gnrstring import slugify
import os


class BaseResourcePrint(BaseResourceBatch):
    """Base resource to make a :ref:`print`"""
    batch_immediate = False
    #dialog_height = '300px'
    #dialog_width = '460px'
    #dialog_height_no_par = '245px'
    html_res = ''
    mail_address = ''
    mail_tags = 'admin'
    templates = '' #CONTROLLARE
    batch_print_modes = ['pdf','server_print','mail_pdf','mail_deliver']
    batch_mail_modes = ['mail_pdf','mail_deliver']
    def __init__(self, *args, **kwargs):
        super(BaseResourcePrint, self).__init__(**kwargs)
        batch_print_modes = self.db.application.getPreference('.print.modes',pkg='sys')
        if batch_print_modes:
            self.batch_print_modes = batch_print_modes.split(',')
        if self.html_res:
            self.htmlMaker = self.page.site.loadTableScript(page=self.page, table=self.maintable,
                                                        respath=self.html_res, class_name='Main')
        else:
            self.htmlMaker = None
        if not hasattr(self, 'mail_tags'):
            self.mail_tags = 'mail'

    def _pre_process(self):
        self.pre_process()
        self.batch_options = self.batch_parameters['batch_options']
        self.print_mode = self.batch_options['print_mode']
        self.server_print_options = self.batch_parameters['_printerOptions']
        self.print_options = self.batch_options[self.print_mode]
        self.print_handler = self.page.getService('print')
        self.pdf_make = self.print_mode != 'client_print'

    def print_selection(self, thermo_selection=None, thermo_record=None):
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
        if not self.get_selection():
            return
        for k,record in self.btc.thermo_wrapper(records, maximum=len(self.get_selection()),enum=True ,**thermo_s):
            self.print_record(record=record, thermo=thermo_r, storagekey=record[pkeyfield],idx=k)

    def print_record(self, record=None, thermo=None, storagekey=None,idx=None):
        result = self.do_print_record(record=record)
        self.onRecordExit(record)
        if result:
            self.storeResult(storagekey, result, record, filepath=getattr(self.htmlMaker,'filepath',result))

    def do_print_record(self,record=None,idx=None,thermo=None):
        result = None
        if self.htmlMaker.cached:
            self.htmlMaker.record = record
            result = self.htmlMaker.getPdfPath()
            self.htmlMaker.filepath = result
            if not os.path.isfile(result):
                result = None
        if not result:
            result = self.htmlMaker(record=record,record_idx=idx, thermo=thermo, pdf=self.pdf_make,
                                **self.batch_parameters)
        return result
    
    def onRecordExit(self, record=None):
        """Hook method.
        
        :param record: the result records of the executed batch"""
        pass
        
    def do(self):
        self.print_selection()
    
        
    def get_record_caption(self, item, progress, maximum, **kwargs):
        caption = '%s (%i/%i)' % (self.tblobj.recordCaption(item),
                                  progress, maximum)
        return caption
        
    def result_handler(self):
        resultAttr = dict()
        result = getattr(self, 'result_handler_%s' % self.print_mode)(resultAttr)
        result = result or ''
        return result, resultAttr
        
    def result_handler_mail_deliver(self, resultAttr):
        mailmanager = self.page.getService('mail')
        mailpars = dict()
        mailpars.update(self.mail_preference.asDict(True))
        mailpars.update(self.print_options.asDict(True))

        for pkey, result in self.results.items():
            record = self.records[pkey]
            mailpars['attachments'] = [result]
            mailpars['to_address'] = record[self.mail_address]
            mailmanager.sendmail(**mailpars)

    def result_handler_mail_pdf(self, resultAttr):
        mailmanager = self.page.getService('mail')
        mailpars = dict()
        mailpars.update(self.mail_preference.asDict(True))
        mailpars.update(self.print_options.asDict(True))
        mailpars['attachments'] = self.results.values()
        mailmanager.sendmail(**mailpars)
        
    def result_handler_server_print(self, resultAttr):
        printer = self.print_handler.getPrinterConnection(self.server_print_options.pop('printer_name'),
                                                          **self.server_print_options.asDict(True))
        return printer.printCups(self.results.values(), self.batch_title)


    def result_handler_html(self, resultAttr):
        print x
        
    def result_handler_pdf(self, resultAttr):
        pdfprinter = self.print_handler.getPrinterConnection('PDF', self.print_options)
        save_as = slugify(self.print_options['save_as'] or self.batch_title)
        filename = pdfprinter.printPdf(self.results.values(), self.batch_title,
                                       outputFilePath=self.page.site.getStaticPath('user:output', 'pdf', save_as,
                                                                                   autocreate=-1))
        if filename:
            self.fileurl = self.page.site.getStaticUrl('user:output', 'pdf', filename, nocache=True, download=True)
            resultAttr['url'] = self.fileurl
            resultAttr['document_name'] = save_as
            resultAttr['url_print'] = 'javascript:genro.openWindow("%s","%s");' %(self.page.site.getStaticUrl('user:output', 'pdf', filename, nocache=True),save_as)
            if self.batch_immediate:
                resultAttr['autoDestroy'] = 5
            if self.batch_immediate is True:
                self.batch_immediate = self.batch_parameters.get('immediate_mode')
            if self.batch_immediate=='print':
                self.page.setInClientData(path='gnr.clientprint',value=self.page.site.getStaticUrl('user:output', 'pdf', filename, nocache=True),fired=True)
            elif self.batch_immediate=='download':
                self.page.setInClientData(path='gnr.downloadurl',value=self.page.site.getStaticUrl('user:output', 'pdf', filename, nocache=True),fired=True)

    def table_script_option_pane(self, pane,print_modes=None, mail_modes=None,**kwargs):
        frame = pane.framePane(height='220px',width='400px')
        frame.dataFormula('#table_script_runner.dialog_options.title','dlgtitle',dlgtitle='!!Print Options',_onBuilt=True)
        frame.data('.print_mode',print_modes[0])
        frame.top.slotToolbar('*,stackButtons,*',stackButtons_font_size='.9em')
        sc = frame.center.stackContainer(selectedPage='^.print_mode')
        for pm in print_modes:
            if pm in mail_modes:
                if not (self.current_batch.mail_tags \
                    and self.application.checkResourcePermission(self.current_batch.mail_tags,self.userTags)):
                    continue
            getattr(self,'table_script_options_%s' %pm)(sc.contentPane(title=pm,pageName=pm,datapath='.%s' %pm),**kwargs)
            
    def table_script_option_common(self,fb,askLetterhead=None,**kwargs):
        if askLetterhead:
            fb.dbSelect(dbtable='adm.htmltemplate', value='^.letterhead_id',
                    lbl='!!Letterhead',hasDownArrow=True)
        fb.simpleTextArea(value='^#table_script_runner.data.batch_note',colspan=5,lbl='!!Notes',height='20px',lbl_vertical_align='top')

    def table_script_options_server_print(self, pane,resource_name=None,**kwargs):
        pane.attributes.update(title='!!Server Print')
        fb = self.table_script_fboptions(pane)
        self.server_print_option_fb(fb, resource=resource_name)

    def table_script_options_pdf(self, pane,**kwargs):
        pane.attributes.update(title='!!Pdf')
        fb = self.table_script_fboptions(pane)
        self.table_script_option_common(fb,**kwargs)
        fb.data('.zipped', False)
        fb.textbox(value='^.save_as', lbl='!!File Name', width='100%')
        fb.checkbox(value='^.zipped', label='!!Zip folder')

    def table_script_options_mail_pdf(self, pane,**kwargs):
        pane.attributes.update(title='!!Pdf by email')
        fb = self.table_script_fboptions(pane)
        self.table_script_option_common(fb,**kwargs)
        fb.textbox(value='^.to_address', lbl='!!To')
        fb.textbox(value='^.cc_address', lbl='!!CC')
        fb.textbox(value='^.subject', lbl='!!Subject')
        fb.simpleTextArea(value='^.body', lbl='!!Body', height='5ex', lbl_vertical_align='top')

    def table_script_options_mail_deliver(self, pane,**kwargs):
        pane.attributes.update(title='!!Deliver mail')
        fb = self.table_script_fboptions(pane)
        self.table_script_option_common(fb,**kwargs)
        fb.textbox(value='^.cc_address', lbl='!!CC', width='100%')
        fb.textbox(value='^.subject', lbl='!!Subject', width='100%')
        fb.simpleTextArea(value='^.body', lbl='!!Body', height='8ex', lbl_vertical_align='top')

    def table_script_fboptions(self, pane, fld_width='100%', tdl_width='4em', **kwargs):
        return pane.div(padding='10px').formbuilder(cols=1, width='100%', tdl_width=tdl_width,
                                                                    border_spacing='4px', fld_width=fld_width)

    def table_script_option_footer(self,pane,**kwargs):
        bar = pane.slotBar('*,cancelbtn,3,confirmbtn,3',_class='slotbar_dialog_footer')
        bar.cancelbtn.slotButton('!!Cancel',action='FIRE .cancel;')
        bar.confirmbtn.slotButton('!!Print', action='FIRE .confirm;')
        return bar
        
    def table_script_parameters_footer(self,pane, immediate=None,**kwargs):
        if immediate:
            bar = pane.slotBar('*,cancelbtn,3,downloadbtn,3,printbtn,3',_class='slotbar_dialog_footer')
            bar.cancelbtn.slotButton('!!Cancel',action='FIRE .cancel;')
            bar.downloadbtn.slotButton('!!Download', action="""SET #table_script_runner.data.immediate_mode ="download";  
                                                               FIRE .confirm ="download";""")
            bar.printbtn.slotButton('!!Print', action="""SET #table_script_runner.data.immediate_mode ="print";  
                                                         FIRE .confirm ="print";""")
            if immediate=='print':
                bar.replaceSlots('downloadbtn,3','')
            elif immediate=='download':
                bar.replaceSlots('printbtn,3','')
        else:
            bar = pane.slotBar('*,cancelbtn,3,confirmbtn,3',_class='slotbar_dialog_footer')
            bar.cancelbtn.slotButton('!!Cancel',action='FIRE .cancel;')
            bar.confirmbtn.slotButton('!!Confirm', action='FIRE .confirm;')
        return bar

    def get_template(self,template_address):
        if not ':' in template_address:
            template_address = 'adm.userobject.data:%s' %template_address
        return self.page.loadTemplate(template_address,asSource=True)[0]


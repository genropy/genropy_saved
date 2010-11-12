#!/usr/bin/env python
# encoding: utf-8
"""
mail.py

Created by Francesco Porcari on 2010-10-16.
Copyright (c) 2010 Softwell. All rights reserved.
"""

from gnr.web.batch.btcbase import BaseResourceBatch
from gnr.core.gnrbag import Bag
from gnr.core.gnrstring import templateReplace
from gnr.core.gnrbaghtml import BagToHtml
import re

class BaseResourceMail(BaseResourceBatch):
    def __init__(self,*args,**kwargs):
        super(BaseResourceMail,self).__init__(**kwargs)
        self.mail_handler = self.page.getService('mail')
        self.mail_preference = self.page.getUserPreference('mail',pkg='adm') or Bag(self.page.application.config.getNode('mail').attr)
        
    def send_one_mail(self, chunk, **kwargs):
        mp = self.mail_pars
        self.mail_handler.sendmail_template(chunk, to_address=mp['to_address'] or chunk[self.doctemplate['meta.to_address']],
                         body=self.doctemplate['content'],subject=self.doctemplate['meta.subject'],
                         cc_address=mp['cc_address'], bcc_address=mp['bcc_address'], from_address=mp['from_address'], 
                         attachments=mp['attachments'], account=mp['account'],
                         host=mp['host'], port=mp['port'], user=mp['user'], password=mp['password'],
                         ssl=mp['ssl'], tls=mp['tls'], html=True,  async=True)
    
class TemplateMail(BaseResourceMail):
    dialog_height = '450px'
    dialog_width = '650px'
    batch_prefix = 'SM'
    batch_title = 'Send Mail'
    batch_cancellable = False
    batch_delay = 0.5
    virtual_columns = ''
    
    def get_record_caption(self,item,progress,maximum,**kwargs):
        caption = '%s (%i/%i)' % (self.tblobj.recordCaption(item),
                              progress,maximum)
        return caption
    
    def cleanTemplate(self,doctemplate_content):
        EXTRACT_FIELDS_STRIPPED_RE=r'(?:\$)(.*?)(?:<|\s)'
        EXTRACT_FIELDS_RE=r'(\$.*?)(?:<|\s)'
        SUB_SPAN_RE=r'(<span\s+class="tplfieldpath".*?/span>\s*<span\s+class="tplfieldcaption".*?/span>)'
        extract_fields_stripped=re.compile(EXTRACT_FIELDS_STRIPPED_RE)
        sub_span=re.compile(SUB_SPAN_RE)
        extract_fields=re.compile(EXTRACT_FIELDS_RE)
        def replace_span(a):
            b = a.group()
            if 'virtual_column' in b:
                self.template_virtual_columns.append(b.split('fieldpath="')[1].split('"')[0])
            return ' '.join(extract_fields.findall(a.group(0),re.MULTILINE))
        return sub_span.sub(replace_span,doctemplate_content)

    def _pre_process(self):
        self.template_virtual_columns = []
        self.mailbody = self.cleanTemplate(self.batch_parameters['body'])
        custom_virtual_columns = self.virtual_columns
        self.virtual_columns = ','.join(self.template_virtual_columns)
        if custom_virtual_columns:
            self.virtual_columns = '%s,%s' %(self.virtual_columns,custom_virtual_columns)
        print self.virtual_columns
        self.htmlBuilder = BagToHtml(templates=self.batch_parameters['htmltemplate'],
                                    templateLoader=self.db.table('adm.htmltemplate').getTemplate)
        
        
    def do(self):
        thermo_s = dict(line_code='selection',message=self.get_record_caption)
        mailpars = dict()
        mailpars.update(self.mail_preference.asDict(True))
        for record in self.btc.thermo_wrapper(self.get_records(),maximum=len(self.get_selection()),**thermo_s):            
            mailpars['html'] = True
            mailpars['body'] = self.htmlBuilder(htmlContent=templateReplace(self.mailbody,record))
            mailpars['to_address'] = record[self.batch_parameters['deliver_field']]
            mailpars['cc_address'] = self.batch_parameters['cc_address']
            mailpars['subject'] = self.batch_parameters['subject']
            self.mail_handler.sendmail(**mailpars)

        
    def table_script_parameters_pane(self,pane,**kwargs):
        #pane.data('gnr.batch.mailbase.tableTree',self.db.tableTreeBag(['sys'],omit=True))
        bc = pane.borderContainer()
        top = bc.contentPane(region='top')
        bc.data('.#parent.zoomFactor',.5)
        fb = top.div(margin_right='5px').formbuilder(cols=2,width='100%',border_spacing='4px',fld_width='100%')
        fb.dbSelect(dbtable='adm.doctemplate',value='^.doctemplate',lbl='Template',
                    condition='maintable=:mt',condition_mt = self.maintable,hasDownArrow=True)
        fb.dbSelect(dbtable='adm.htmltemplate',value='^.htmltemplate_id',
                    selected_name='.htmltemplate',
                    lbl='Header template',hasDownArrow=True)
        fb.dataRpc('.#parent.rendered_template','table_script_renderTemplate',doctemplate_id='^.doctemplate',
                    htmltemplate='^.htmltemplate',record_id= '==genro.wdgById(_gridId).rowIdByIndex(_idx);',
                    _idx='^list.rowIndex',_gridId='maingrid',_if='doctemplate_id')
        fb.dataRecord('.#parent.currentDocTemplate','adm.doctemplate',
                        pkey='^.doctemplate',_if='pkey',_onResult="""
                                                                    var record = result.getValue();
                                                                    SET .subject = record.getItem("metadata.subject"); 
                                                                    SET .deliver_field = record.getItem("metadata.to_address");
                                                                    SET .body = record.getItem('content');
                                                                    """)
        fb.textbox(value='^.cc_address',lbl='!!CC',colspan=2)
        fb.textbox(value='^.subject',lbl='!!Subject',colspan=2)
        sc = bc.stackContainer(region='center',selectedPage='^.#parent.previewPage')
        preview = sc.contentPane(pageName='preview',_class='preview')
        toolbar = preview.toolbar()
        preview.div(height='100%',overflow='auto').div(innerHTML='^.#parent.rendered_template',zoomFactor='^.#parent.zoomFactor',
                                                        margin='10px',background_color='white')
        toolbar.button('Edit',iconClass='icnBaseEdit',float='right',
                        action='SET .#parent.previewPage = "edit";',showLabel=False)
        toolbar.horizontalSlider(value='^.#parent.zoomFactor', minimum=0, maximum=1,
                                intermediateChanges=True,width='15em',float='right')
        toolbar.data('list.rowIndex',0)
        toolbar.button('!!Previous', action='SET list.rowIndex = idx-1;', idx='=list.rowIndex',
                        iconClass="tb_button icnNavPrev",  showLabel=False)
        toolbar.button('!!Next', action='SET list.rowIndex = idx+1;', idx='=list.rowIndex',
                        iconClass="tb_button icnNavNext", disabled='^form.atEnd', showLabel=False)
        
        editpane = sc.borderContainer(pageName='edit')
        editpane.contentPane(region='top').toolbar().button('Preview',iconClass='icnBaseEdit',float='right',
                                    action='SET .#parent.previewPage = "preview";',
                                    showLabel=False)
        self.RichTextEditor(editpane.contentPane(region='center'), 
                            config_contentsCss=self.getResourceUri('doctemplate.css',add_mtime=True),
                            value='^.body',toolbar=self.rte_toolbar_standard())
         
  #INSIDE BATCHHANDLER
  # def rpc_table_script_renderTemplate(self,record_id=None,doctemplate_id=None,htmltemplate=None):
  #     doctemplateRecord = self.db.table('adm.doctemplate').record(pkey=doctemplate_id).output('bag')        
  #     virtual_columns = doctemplateRecord['virtual_columns']
  #     record = self.tblobj.record(pkey=record_id,virtual_columns=virtual_columns)
  #     doctemplate = doctemplateRecord['content']
  #     htmlContent = templateReplace(doctemplate,record,True)
  #     htmlbuilder = BagToHtml(templates=htmltemplate,templateLoader=self.db.table('adm.htmltemplate').getTemplate)
  #     html = htmlbuilder(htmlContent=htmlContent)
  #     return html
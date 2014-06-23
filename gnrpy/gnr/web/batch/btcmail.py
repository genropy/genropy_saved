#!/usr/bin/env python
# encoding: utf-8
#
#btcmail.py
#
#Created by Francesco Porcari on 2010-10-16.
#Copyright (c) 2011 Softwell. All rights reserved.

from gnr.web.batch.btcbase import BaseResourceBatch
from gnr.core.gnrbag import Bag
from datetime import datetime

class BaseResourceMail(BaseResourceBatch):
    def __init__(self, *args, **kwargs):
        super(BaseResourceMail, self).__init__(**kwargs)
        self.mail_handler = self.page.getService('mail')
        self.mail_preference = Bag(self.mail_handler.getDefaultMailAccount())

    def send_one_template(self,record=None,to_address=None,cc_address=None,subject=None,body=None,attachments=None,**kwargs):
        self.mail_handler.sendmail_template(record,body=body,to_address=to_address,attachments=attachments,
                                            cc_address=cc_address,subject=subject,**kwargs)

    def send_one_email(self,to_address=None,cc_address=None,subject=None,body=None,attachments=None,_record_id=None):
        mp = self.mail_preference
        mail_code = self.batch_parameters.get('mail_code')
        tbl = self.tblobj.fullname
        now = datetime.now()
        try:
            self.mail_handler.sendmail(to_address=to_address,
                                    body=body, subject=subject,
                                    cc_address=cc_address, bcc_address=mp['bcc_address'],
                                    from_address=mp['from_address'],
                                    attachments=attachments or mp['attachments'], 
                                    account=mp['account'],
                                    smtp_host=mp['smtp_host'], port=mp['port'], user=mp['user'], password=mp['password'],
                                    ssl=mp['ssl'], tls=mp['tls'], html=mp['html'], async=False)
            
            with self.db.tempEnv(connectionName='system',storename=self.db.rootstore):
                self.db.table('adm.sent_email').insert(dict(code=mail_code,tbl=tbl,mail_address=to_address,sent_ts=now,record_id=_record_id))
                self.db.commit()

        except Exception:
            print 'failure in email',to_address
            with self.db.tempEnv(connectionName='system',storename=self.db.rootstore):
                self.db.table('adm.sent_email').insert(dict(code=mail_code,tbl=tbl,mail_address=to_address,sent_ts=None,_record_id=_record_id))
                self.db.commit()
        
    def get_template(self,template_address):
        if not ':' in template_address:
            template_address = 'adm.userobject.data:%s' %template_address
        return self.page.loadTemplate(template_address,asSource=True)[0]

    def get_selection(self,**kwargs):
        selection = super(BaseResourceMail, self).get_selection(**kwargs)
        mail_code = self.batch_parameters.get('mail_code')
        if not mail_code:
            return selection
        tbl = self.tblobj.fullname
        sending_pkeys = selection.output('pkeylist')
        sent = self.db.table('adm.sent_email').query(where='$tbl=:tbl AND $code=:c AND $sent_ts IS NOT NULL AND $record_id IN :spk',
                                        tbl=tbl,c=mail_code,spk=sending_pkeys,
                                        columns='$record_id').fetch()
        if not sent:
            return selection
        sent = set([r['record_id'] for r in sent])
        sending_pkeys = set(sending_pkeys)
        sending_pkeys = sending_pkeys.difference(sent)
        return self.tblobj.query(where='$%s IN :pk' %self.tblobj.pkey,pk=sending_pkeys,excludeDraft=False,**kwargs).selection()

                                            

class TemplateMail(BaseResourceMail):
    dialog_height = '450px'
    dialog_width = '650px'
    batch_prefix = 'SM'
    batch_title = 'Send Mail'
    batch_cancellable = False
    batch_delay = 0.5
    virtual_columns = ''

    def get_record_caption(self, item, progress, maximum, **kwargs):
        caption = '%s (%i/%i)' % (self.tblobj.recordCaption(item),
                                  progress, maximum)
        return caption

    def _pre_process(self):
        self.doctemplate_tbl = self.db.table('adm.doctemplate')
        self.htmlBuilder = self.doctemplate_tbl.getTemplateBuilder(doctemplate=self.batch_parameters.get('doctemplate'),
                                                                   templates=self.batch_parameters.get('templates'))

    def do(self):
        thermo_s = dict(line_code='selection', message='sending')
        mailpars = dict()
        mailpars.update(self.mail_preference.asDict(True))
        pkeys = self.get_selection_pkeys()
        for pkey in self.btc.thermo_wrapper(pkeys, **thermo_s):
            mailpars['html'] = True
            mailpars['body'] = self.doctemplate_tbl.renderTemplate(self.htmlBuilder, record_id=pkey)
            record = self.htmlBuilder.record
            mailpars['to_address'] = record[self.batch_parameters.get('to_address')]
            mailpars['cc_address'] = self.batch_parameters.get('cc_address')
            mailpars['subject'] = self.batch_parameters.get('subject')
            self.mail_handler.sendmail(**mailpars)


    def table_script_parameters_pane(self, pane, **kwargs):
        #pane.data('gnr.batch.mailbase.tableTree',self.db.tableTreeBag(['sys'],omit=True))
        bc = pane.borderContainer()
        top = bc.contentPane(region='top')
        bc.data('.#parent.zoomFactor', .5)
        fb = top.div(margin_right='5px').formbuilder(cols=2, width='100%', border_spacing='4px', fld_width='100%')
        fb.dbSelect(dbtable='adm.doctemplate', value='^.doctemplate_id', lbl='Template',
                    condition='maintable=:mt', condition_mt=self.maintable, hasDownArrow=True)
        fb.dbSelect(dbtable='adm.htmltemplate', value='^.htmltemplate_id',
                    selected_name='.templates',
                    lbl='Header template', hasDownArrow=True)
        #doctemplate=None,record_id=None,templates=None
        fb.dataRpc('.#parent.rendered_template', 'table_script_renderTemplate',
                   templates='^.templates',
                   doctemplate='=.doctemplate', doctemplate_id='=.doctemplate_id',
                   record_id='==genro.wdgById(_gridId).rowIdByIndex(_idx);',
                   _idx='^list.rowIndex',
                   _gridId='maingrid',
                   _if='doctemplate_id', _fired='^.doctemplate_loaded')
        fb.dataRecord('.doctemplate', 'adm.doctemplate', pkey='^.doctemplate_id', _if='pkey',
                      _onResult="""
                            var metadata = result.getValue('metadata');
                            if(metadata){
                                SET .to_address = metadata.getItem('to_address');
                                SET .subject = metadata.getItem('subject');
                            }
                            FIRE .doctemplate_loaded;
                        """)
        fb.textbox(value='^.cc_address', lbl='!!CC', colspan=2)
        fb.textbox(value='^.subject', lbl='!!Subject', colspan=2)
        sc = bc.stackContainer(region='center', selectedPage='^.#parent.previewPage')
        preview = sc.contentPane(pageName='preview', _class='preview')
        toolbar = preview.toolbar()
        preview.div(height='100%', overflow='auto').div(innerHTML='^.#parent.rendered_template',
                                                        zoomFactor='^.#parent.zoomFactor',
                                                        margin='10px', background_color='white')
        toolbar.button('Edit', iconClass='icnBaseEdit', float='right',
                       action='SET .#parent.previewPage = "edit";', showLabel=False)
        toolbar.horizontalSlider(value='^.#parent.zoomFactor', minimum=0, maximum=1,
                                 intermediateChanges=True, width='15em', float='right')
        toolbar.data('list.rowIndex', 0)
        toolbar.button('!!Previous', action='SET list.rowIndex = idx-1;', idx='=list.rowIndex',
                       iconClass="tb_button icnNavPrev", showLabel=False)
        toolbar.button('!!Next', action='SET list.rowIndex = idx+1;', idx='=list.rowIndex',
                       iconClass="tb_button icnNavNext", disabled='^form.atEnd', showLabel=False)

        editpane = sc.borderContainer(pageName='edit')
        editpane.contentPane(region='top').toolbar().button('Preview', iconClass='icnBaseEdit', float='right',
                                                            action='SET .#parent.previewPage = "preview";',
                                                            showLabel=False)
        self.RichTextEditor(editpane.contentPane(region='center'),
                            config_contentsCss=self.getResourceUri('doctemplate.css', add_mtime=True),
                            value='^.doctemplate.content', toolbar=self.rte_toolbar_standard())



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
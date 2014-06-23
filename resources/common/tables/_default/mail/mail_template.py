# -*- coding: UTF-8 -*-

# test_special_action.py
# Created by Francesco Porcari on 2010-07-02.
# Copyright (c) 2010 Softwell. All rights reserved.

from gnr.web.batch.btcmail import BaseResourceMail
from gnr.web.gnrbaseclasses import TableScriptToHtml
from gnr.core.gnrstring import templateReplace
from gnr.core.gnrbag import Bag

tags='system'

class Main(BaseResourceMail):
    batch_prefix = 'mail_tpl'
    batch_cancellable = True
    batch_delay = 0.5
    batch_immediate = True
    batch_title = None
    templates = ''
        
    def do(self):
        self.sendmail_selection()
        
    def sendmail_selection(self, thermo_selection=None, thermo_record=None):
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
        for record in self.btc.thermo_wrapper(records, maximum=len(self.get_selection()), **thermo_s):
            self.sendmail_record(record=record, thermo=thermo_r, storagekey=record[pkeyfield])
    
    def pre_process(self):
        extra_parameters = self.batch_parameters.pop('extra_parameters')
        self.maintable = extra_parameters['table']
        pkg,table = self.maintable.split('.')
        template_address = extra_parameters['template_address'] or extra_parameters['template_id']
        data = self.get_template(template_address)
        self.compiledTemplate = Bag(data['compiled'])
        self.mail_pars = Bag(data['metadata.email_compiled'])
        self.mail_pars['attachments'] = self.mail_pars.pop('attachments') if 'attachments' in self.mail_pars else ''
        self.batch_parameters.setdefault('letterhead_id',data.getItem('metadata.default_letterhead'))
        self.batch_parameters.setdefault('as_pdf',False)
        self.batch_title = data['summary'] or 'Mail'
        self.tblobj = self.db.table(self.maintable)
        self.virtual_columns =  self.compiledTemplate.getItem('main?virtual_columns') 
        self.mail_preference['html'] = not self.batch_parameters['as_pdf']
        self.htmlMaker = TableScriptToHtml(self.page,self.tblobj)
            
    def sendmail_record(self, record=None, thermo=None, storagekey=None,**kwargs):
        record.update(self.batch_parameters)
        as_pdf = self.batch_parameters['as_pdf']
        to_address = templateReplace(self.mail_pars.getItem('to_address',''),record)
        subject = templateReplace(self.mail_pars.getItem('subject',''),record)
        cc_address = templateReplace(self.mail_pars.getItem('cc_address',''),record)

        htmlContent=templateReplace(self.compiledTemplate,record, 
                                    safeMode=True,noneIsBlank=False,
                                    locale=self.page.locale,
                                    formats=self.compiledTemplate.getItem('main?formats'),
                                    masks=self.compiledTemplate.getItem('main?masks'),
                                    localizer=self.page.localizer)
                                    
        result = self.htmlMaker(htmlContent=htmlContent,
                                filename='%s.html' %record['id'],
                                record=record, thermo=thermo, pdf=as_pdf,
                                **self.batch_parameters)
        if result:
            attachments = templateReplace(self.mail_pars.getItem('attachments',''),record)
            attachments = attachments.split(',') if attachments else []
            body = None
            if as_pdf:
                attachments.append(result)
                body = ''
            else:
                body = result
                attachments = attachments or None
            self.send_one_email(to_address=to_address,cc_address=cc_address,subject=subject,body=body,attachments=attachments,_record_id=record[self.tblobj.pkey])
        
    def table_script_parameters_pane(self,pane,extra_parameters=None,record_count=None,**kwargs):
        pkg,tbl= extra_parameters['table'].split('.')
        pane = pane.div(padding='10px',min_height='60px')
        template_address = extra_parameters['template_address'] or 'adm.userobject.data:%s' %extra_parameters['template_id']
        data =  self.loadTemplate(template_address,asSource=True)[0]
        #data,meta = self.db.table('adm.userobject').loadUserObject(pkey=extra_parameters['template_id'])
        pane.dataFormula('#table_script_runner.dialog_pars.title','dlgtitle',
                            dlgtitle='!!%s (%i)' %(data['metadata.summary'] or 'Mail',record_count),_onBuilt=True)
        fb = pane.formbuilder(cols=1,fld_width='20em',border_spacing='4px')
        fb.dbSelect(dbtable='adm.htmltemplate', value='^.letterhead_id',lbl='!!Letterhead',hasDownArrow=True)
        fb.checkbox(value='^.as_pdf',label='!!Send as pdf')
        fb.dataController("SET .letterhead_id = default_letterhead || null;",_onBuilt=True,
                            default_letterhead=data.getItem('metadata.default_letterhead') or False,_if='default_letterhead')
        fb.textbox(value='^.mail_code',lbl='Mail code')
        if data.getItem('parameters'):
            parameters = data.getItem('parameters')
            fielddict = {'T':'Textbox','L':'NumberTextBox','D':'DateTextBox','B':'Checkbox','N':'NumberTextBox', 'TL':'Simpletextarea'}
            for n in parameters:
                attr = n.attr
                values=attr.get('values')
                mandatory = attr.get('mandatory') == 'T'
                kwargs = dict(value='^.%s' %attr['code'],lbl=attr['description'] or attr['code'], validate_notnull=mandatory)
                if values:
                    tag = 'filteringSelect'
                    kwargs['values'] = values
                else:
                    tag = fielddict[attr.get('fieldtype') or 'T']
                if tag == 'Simpletextarea':
                    kwargs['lbl_vertical_align']='top'
                    kwargs['colspan'] = 2
                kwargs['tag'] =tag
                fb.child(**kwargs)
# -*- coding: UTF-8 -*-

# test_special_action.py
# Created by Francesco Porcari on 2010-07-02.
# Copyright (c) 2010 Softwell. All rights reserved.

from gnr.web.batch.btcprint import BaseResourcePrint
from gnr.web.gnrbaseclasses import TableScriptToHtml
from gnr.core.gnrstring import templateReplace
from gnr.core.gnrbag import Bag

tags='system'
class Main(BaseResourcePrint):
    batch_prefix = 'pr_tpl'
    batch_cancellable = True
    batch_delay = 0.5
    batch_immediate = True
    batch_title = None
    print_mode = 'pdf'
    
    def pre_process(self):
        extra_parameters = self.batch_parameters.pop('extra_parameters')
        self.maintable = extra_parameters['table']
        pkg,table = self.maintable.split('.')
        template_address = extra_parameters['template_address'] or extra_parameters['template_id']
        data = self.get_template(template_address)
        self.compiledTemplate = Bag(data['compiled'])
        self.batch_parameters.setdefault('letterhead_id',data['metadata.default_letterhead'])
        self.batch_title = data['summary'] or 'Print'
        self.tblobj = self.db.table(self.maintable)
        self.virtual_columns =  self.compiledTemplate.getItem('main?virtual_columns') 
        self.htmlMaker = TableScriptToHtml(self.page,self.tblobj)
            
    def print_record(self, record=None, thermo=None, storagekey=None,**kwargs):
        record.update(self.batch_parameters)
        htmlContent=templateReplace(self.compiledTemplate,record, 
                                    safeMode=True,noneIsBlank=False,
                                    locale=self.page.locale,
                                    formats=self.compiledTemplate.getItem('main?formats'),
                                    masks=self.compiledTemplate.getItem('main?masks'),
                                    dtypes=  self.compiledTemplate.getItem('main?dtypes'),
                                    localizer=self.page.localizer,
                                    urlformatter=self.page.externalUrl)
        result = self.htmlMaker(htmlContent=htmlContent,
                                filename='%s.html' %record['id'],
                                record=record, thermo=thermo, pdf=self.pdf_make,
                                **self.batch_parameters)
        if result:
            self.storeResult(storagekey, result, record, filepath=self.htmlMaker.filepath)        
        
    def table_script_parameters_pane(self,pane,extra_parameters=None,record_count=None,**kwargs):
        pkg,tbl= extra_parameters['table'].split('.')
        pane = pane.div(padding='10px',min_height='60px')        
        template_address = extra_parameters['template_address'] or 'adm.userobject.data:%s' %extra_parameters['template_id']
        data =  self.loadTemplate(template_address,asSource=True)[0]
        #data,meta = self.db.table('adm.userobject').loadUserObject(pkey=extra_parameters['template_id'])
        pane.dataFormula('#table_script_runner.dialog_pars.title','dlgtitle',
                            dlgtitle='!!%s (%i)' %(data['metadata.summary'] or 'Print',record_count),_onBuilt=True)
        fb = pane.formbuilder(cols=1,fld_width='20em',border_spacing='4px')
        fb.dbSelect(dbtable='adm.htmltemplate', value='^.letterhead_id',lbl='!!Letterhead',hasDownArrow=True)
        fb.dataController("SET .letterhead_id = default_letterhead || null;",_onBuilt=True,
                            default_letterhead=data.getItem('metadata.default_letterhead') or False,_if='default_letterhead')
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
# -*- coding: UTF-8 -*-

# test_special_action.py
# Created by Francesco Porcari on 2010-07-02.
# Copyright (c) 2010 Softwell. All rights reserved.

from gnr.web.batch.btcprint import BaseResourcePrint
from gnr.web.gnrbaseclasses import TableScriptToHtml
from gnr.core.gnrstring import templateReplace
from gnr.core.gnrbag import Bag

class Main(BaseResourcePrint):
    batch_prefix = 'pr_tpl'
    batch_cancellable = True
    batch_delay = 0.5
    batch_immediate = True
    
    def pre_process(self):
        extra_parameters = self.batch_parameters.pop('extra_parameters')
        self.maintable = extra_parameters['table']
        pkg,table = self.maintable.split('.')
        data,meta = self.db.package(pkg).loadUserObject(pkey=extra_parameters['template_id'])
        self.compiledTemplate = Bag(data['compiled'])
        self.batch_title = meta['description'] or meta['code']
        self.tblobj = self.db.table(self.maintable)
        self.virtual_columns =  self.compiledTemplate.getItem('main?virtual_columns')        
        self.htmlMaker = TableScriptToHtml(self.page,self.tblobj)
        
    def print_record(self, record=None, thermo=None, storagekey=None):
        """add???
        
        :param record: add???
        :param thermo: add???
        :param storagekey: add???"""
        record.update(self.batch_parameters)
        htmlContent=templateReplace(Bag(self.compiledTemplate),record, 
                                    safeMode=True,noneIsBlank=False,
                                    locale=self.htmlMaker.locale,
                                    formats=self.compiledTemplate.getItem('main?formats'))
        result = self.htmlMaker(htmlContent=htmlContent,
                                record=record, thermo=thermo, pdf=self.pdf_make,
                                **self.batch_parameters)
        if result:
            self.storeResult(storagekey, result, record, filepath=self.htmlMaker.filepath)        
        
    def table_script_parameters_pane(self,pane,extra_parameters=None,**kwargs):
        pkg,tbl= extra_parameters['table'].split('.')
        data,meta = self.db.package(pkg).loadUserObject(pkey=extra_parameters['template_id'])
        if data.getItem('parameters'):
            parameters = data.getItem('parameters')
            fb = pane.div(margin='5px').formbuilder(cols=2,field_width='100%',tdl_width='8em',border_spacing='2px',width='100%')
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
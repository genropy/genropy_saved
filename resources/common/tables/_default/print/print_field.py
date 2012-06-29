# -*- coding: UTF-8 -*-

# test_special_action.py
# Created by Francesco Porcari on 2010-07-02.
# Copyright (c) 2010 Softwell. All rights reserved.

from gnr.web.batch.btcprint import BaseResourcePrint
from gnr.web.gnrbaseclasses import TableScriptToHtml

tags='system'
class Main(BaseResourcePrint):
    batch_prefix = 'pr_field'
    batch_cancellable = True
    batch_delay = 0.5
    batch_immediate = 'print'
    batch_title = None
    print_mode = 'pdf'

    def pre_process(self):
        extra_parameters = self.batch_parameters.pop('extra_parameters')
        self.maintable = extra_parameters['table']
        self.tblobj = self.db.table(self.maintable)
        self.fieldToPrint = extra_parameters['print']
        self.fieldDocumentName = extra_parameters['docname'] or self.tblobj.pkey
        self.htmlMaker = TableScriptToHtml(self.page,self.tblobj)
            
    def print_record(self, record=None, thermo=None, storagekey=None,**kwargs):
        result = self.htmlMaker(htmlContent=record[self.fieldToPrint],
                                filename='%s.html' %self.fieldDocumentName,
                                record=record, thermo=thermo, pdf=self.pdf_make,
                                **self.batch_parameters)
        if result:
            self.storeResult(storagekey, result, record, filepath=self.htmlMaker.filepath)        

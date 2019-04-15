# -*- coding: utf-8 -*-

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
    batch_title = 'Print'
    print_mode = 'pdf'

    def pre_process(self):
        extra_parameters = self.batch_parameters.pop('extra_parameters')
        self.maintable = extra_parameters['table']
        self.tblobj = self.db.table(self.maintable)
        self.template_address = extra_parameters['template_address'] or extra_parameters['template_id']
        self.pdfform_service = self.page.site.getService('pdfform')


    def print_record(self, record=None, thermo=None, storagekey=None,**kwargs):
        output = self.page.site.storageNode('page:%s/%s.pdf'%(self.template_address,record['id']))
        self.pdfform_service.fillFromUserObject(userObject=self.template_address,
            table=self.maintable, record_id=record['id'], output=output)
        self.storeResult(storagekey, output, record, filepath=output)


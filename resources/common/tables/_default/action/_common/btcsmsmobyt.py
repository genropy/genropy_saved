# -*- coding: UTF-8 -*-

# test_special_action.py
# Created by Francesco Porcari on 2010-07-02.
# Copyright (c) 2011 Softwell. All rights reserved.
from gnr.web.batch.btcbase import BaseResourceBatch
from gnr.core.gnrbag import Bag
from gnr.core.gnrstring import templateReplace

caption = 'Sms base deliver'
description = 'Sms base template'
tags = 'nobody'
class Main(BaseResourceBatch):
    dialog_height = '450px'
    dialog_width = '650px'
    batch_prefix = 'SS'
    batch_title = 'Send Sms'
    batch_cancellable = False
    batch_delay = 0.5
    virtual_columns = ''

    def __init__(self, *args, **kwargs):
        super(BaseResourceBatch, self).__init__(**kwargs)
        self.sms_handler = self.page.getService('sms')
        self.sms_preference = self.page.getUserPreference('sms', pkg='adm') or Bag(
                self.page.application.config.getNode('sms').attr)

    def get_record_caption(self, item, progress, maximum, **kwargs):
        caption = '%s (%i/%i)' % (self.tblobj.recordCaption(item),
                                  progress, maximum)
        return caption

    def _pre_process(self):
        pass

    def do(self):
        thermo_s = dict(line_code='selection', message='sending')
        smspars = dict()
        smspars.update(self.sms_preference.asDict(True))
        pkeys = self.get_selection_pkeys()
        for pkey in self.btc.thermo_wrapper(pkeys, **thermo_s):
            
            smspars['data'] = templateReplace(value, datasource)
            self.doctemplate_tbl.renderTemplate(self.htmlBuilder, record_id=pkey)
            smspars['receiver'] = record[self.batch_parameters.get('receiver')]
            self.sms_handler.sendsms(**smspars)


    def table_script_parameters_pane(self, pane, **kwargs):
        #pane.data('gnr.batch.mailbase.tableTree',self.db.tableTreeBag(['sys'],omit=True))
        bc = pane.borderContainer()
        top = bc.contentPane(region='top', height='120px')
        fb = top.div(margin_right='5px').formbuilder(cols=2, width='100%', border_spacing='4px', fld_width='100%')
        fb.textbox(value='^.receiver', lbl='!!Receiver', colspan=2)
        self.RichTextEditor(bc.contentPane(region='center'),
                            value='^.content', toolbar=self.rte_toolbar_standard())


# -*- coding: UTF-8 -*-

# test_special_action.py
# Created by Francesco Porcari on 2010-07-02.
# Copyright (c) 2011 Softwell. All rights reserved.

from gnr.web.batch.btcexport import BaseResourceExport

caption = '!!Export'
tags = 'user'
description = '!!Export to xls,cvs,html'

class Main(BaseResourceExport):
    batch_prefix = 'exp'
    batch_title = 'Export'
    batch_cancellable = False
    batch_delay = 0.5
    batch_immediate = True

    def table_script_parameters_pane(self, pane, **kwargs):
        fb = pane.formbuilder(cols=1, border_spacing='3px')
        fb.data('.export_mode', 'xls')
        fb.filteringSelect(value='^.export_mode', values='xls:Excel,csv:Csv,html:Html', lbl='!!Mode')
        fb.textbox(value='^.filename', lbl='!!Save as')
        

# -*- coding: utf-8 -*-
# test_special_action.py
# Created by Francesco Porcari on 2010-07-02.
# Copyright (c) 2010 Softwell. All rights reserved.

from gnr.web.batch.btcaction import BaseResourceAction

caption = 'Import from source'
description='Import data from source'

class Main(BaseResourceAction):
    batch_prefix = 'IM'
    batch_title = 'Import data'
    batch_cancellable = False
    batch_immediate = True
    batch_delay = 0.5

    def do(self):
        pass
        
    def result_handler(self):
        pass

    def table_script_parameters_pane(self,center,**kwargs):
        pass
# -*- coding: utf-8 -*-

# test_special_action.py
# Created by Francesco Porcari on 2010-07-02.
# Copyright (c) 2011 Softwell. All rights reserved.

from gnr.web.batch.btcaction import BaseResourceAction

caption = '!!Update to release'
tags = '_DEV_'
description = '!!Update records to last release'

class Main(BaseResourceAction):
    batch_prefix = 'tch'
    batch_title = 'Update to release'
    batch_cancellable = False
    batch_delay = 0.5
    batch_immediate = True
    
    def do(self):
        if not self.tblobj.getReleases()[0]:
            return
        self.tblobj.updateRecordsToLastRelease_raw(_wrapper=self.btc.thermo_wrapper, _wrapperKwargs=dict(line_code='touch',message = 'Record',tblobj=self.tblobj),commit=self.batch_parameters.get('commit_frequency'))
        self.db.commit()

    def table_script_parameters_pane(self, pane, table=None,**kwargs):
        fb = pane.div(padding='10px').formbuilder(cols=1,border_spacing='3px')
        fb.numbertextbox(value='^.commit_frequency',lbl='Commit Freq')
        
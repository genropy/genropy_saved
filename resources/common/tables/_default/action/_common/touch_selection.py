# -*- coding: UTF-8 -*-

# test_special_action.py
# Created by Francesco Porcari on 2010-07-02.
# Copyright (c) 2011 Softwell. All rights reserved.

from gnr.web.batch.btcaction import BaseResourceAction

caption = '!!Touch Selection'
tags = '_DEV_'
description = '!!Touch Selection'

class Main(BaseResourceAction):
    batch_prefix = 'tch'
    batch_title = 'Touch Selection'
    batch_cancellable = False
    batch_delay = 0.5
    batch_immediate = True
    
    def do(self):
        pkeys = self.get_selection_pkeys()
        wrapper = None
        wrapper_kw = None
        tblobj =self.get_selection().dbtable
        if self.batch_parameters.get('use_thermo'):
            wrapper = self.btc.thermo_wrapper
            wrapper_kw = dict(line_code='touch',message = 'Record',tblobj=tblobj)

        tblobj.touchRecords(_pkeys=pkeys,_wrapper=wrapper,_wrapperKwargs=wrapper_kw,method=self.batch_parameters.get('touchmethod'))
        self.db.commit()

    def table_script_parameters_pane(self, pane, table=None,**kwargs):
        fb = pane.div(padding='10px').formbuilder(cols=1,border_spacing='3px')
        fb.checkbox(value='^.use_thermo',label='Thermo')
        tblobj = self.db.table(table)
        handlers = ['%s:%s' %(k, getattr(tblobj,k).__doc__ or k[6:]) for k in dir(tblobj) if k.startswith('touch_')]
        if handlers:
            fb.filteringSelect(value='^.touchmethod',values=','.join(handlers),lbl='Method')
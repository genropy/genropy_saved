# -*- coding: UTF-8 -*-

# test_special_action.py
# Created by Francesco Porcari on 2010-07-02.
# Copyright (c) 2011 Softwell. All rights reserved.

from gnr.web.batch.btcaction import BaseResourceAction

caption = '!!Set rows values'
tags = '_DEV_'
description = '!!Set rows values'

class Main(BaseResourceAction):
    batch_prefix = 'srv'
    batch_title = 'Set rows value'
    batch_cancellable = False
    batch_delay = 0.5
    batch_immediate = True
    
    def do(self):
        values = self.batch_parameters.get('values')
        updater = dict()
        for k,v in values.items():
            if v is not None:
                updater[k] = v
        self.batchUpdate(updater,_raw_update=True,message='setting_values')
        self.db.commit()

    def table_script_parameters_pane(self, pane, table=None,**kwargs):
        tblobj = self.db.table(table)
        cols = int(len(tblobj.columns)/30)+1
        fb = pane.div(max_height='600px',overflow='auto').formbuilder(margin='5px',cols=cols,border_spacing='3px',dbtable=table,datapath='.values')
        for k,v in tblobj.columns.items():
            attr = v.attributes
            if not (attr.get('_sysfield') or attr.get('dtype') == 'X'):
                fb.field(k,validate_notnull=False,html_label=True)



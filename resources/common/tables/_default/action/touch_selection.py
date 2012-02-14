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
        tblobj =self.get_selection().dbtable
        tblobj.touchRecords(where='$pkey IN :pkeys', pkeys=self.get_selection_pkeys())
        self.db.commit()

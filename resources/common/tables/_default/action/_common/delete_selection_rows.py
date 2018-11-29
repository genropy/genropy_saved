# -*- coding: UTF-8 -*-

# test_special_action.py
# Created by Francesco Porcari on 2010-07-02.
# Copyright (c) 2011 Softwell. All rights reserved.

from gnr.web.batch.btcexport import BaseResourceExport

caption = '!!Delete selection rows'
tags = 'superadmin'
permissions = 'del'
description = '!!Delete selection rows'

class Main(BaseResourceExport):
    batch_prefix = 'delete'
    batch_title = 'Delete selection rows'
    batch_cancellable = False
    batch_delay = 0.5
    batch_immediate = True


    def do(self):
        selection = self.get_selection(columns='*,$__is_protected_row')
        for r in self.btc.thermo_wrapper(selection, 'record'):
            if r.get('__is_protected_row'):
                continue
            self.tblobj.delete(r)
        self.db.commit()
            


    def table_script_parameters_pane(self, pane, **kwargs):
        pane.div('You are going to delete the elements of the current selection')
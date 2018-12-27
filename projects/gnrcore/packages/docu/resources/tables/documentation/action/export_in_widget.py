# -*- coding: utf-8 -*-

# test_special_action.py
# Created by Francesco Porcari on 2010-07-02.
# Copyright (c) 2011 Softwell. All rights reserved.
from gnr.web.batch.btcbase import BaseResourceBatch

caption = 'Export in sys widget'
description = 'Export in sys widget'
tags = '_DEV_'
class Main(BaseResourceBatch):
    dialog_height = '450px'
    dialog_width = '650px'
    batch_prefix = 'ESW'
    batch_title =  'Export in sys widget'
    batch_cancellable = False
    batch_delay = 0.5

    def do(self):
        desttable = self.db.table('sys.widget')
        desttable.sql_deleteSelection(where='$id IS NOT NULL')
        for r in self.tblobj.query(where='$doctype=:w AND $parent_id IS NOT NULL',w='widget',bagFields=True).fetch():
            r = dict(r)
            hierarchical_pkey = r.pop('hierarchical_pkey')
            r.pop('hierarchical_name')
            if len(hierarchical_pkey.split('/'))==2:
                r['parent_id'] = None
            desttable.insert(r)
        self.db.commit()



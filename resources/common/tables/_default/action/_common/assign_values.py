# -*- coding: UTF-8 -*-

# test_special_action.py
# Created by Francesco Porcari on 2010-07-02.
# Copyright (c) 2011 Softwell. All rights reserved.

from gnr.web.batch.btcaction import BaseResourceAction

caption = '!!Assign values'
tags = '_NOBODY_'
description = '!!Assign values'

class Main(BaseResourceAction):
    batch_prefix = 'srv'
    batch_title = 'Set rows value'
    batch_cancellable = True
    batch_delay = 0.5
    batch_immediate = True
    
    def do(self):
        values = self.batch_parameters.get('values')
        do_triggers = self.batch_parameters.get('do_triggers')
        def updater(row):
            for k,v,forced_null,replace in values.digest('#k,#v,#a.force_null,#a.replace'):
                if forced_null:
                    row[k] = None
                elif v is not None and (row[k] is None or replace):
                    row[k] = v
        self.batchUpdate(updater,_raw_update=not do_triggers,message='setting_values')
        self.db.commit()


    def table_script_parameters_pane(self, pane, table=None,**kwargs):
        tblobj = self.db.table(table)
        do_trigger = False
        box = pane.div(max_height='600px',overflow='auto')
        fb = box.formbuilder(margin='5px',cols=3,border_spacing='3px',dbtable=table,datapath='.values')
        for k,v in tblobj.columns.items():
            attr = v.attributes
            batch_assign = attr.get('batch_assign')
            if not batch_assign:
                continue
            auth = 'user'
            kw = {}
            if batch_assign is not True:
                kw.update(batch_assign)
            if not self.application.checkResourcePermission(kw.pop('tags',None),self.userTags):
                continue
            do_trigger = kw.pop('do_trigger',False) or do_trigger
            fb.field(k,validate_notnull=False,html_label=True,zoom=False,lbl_fieldname=k,
                        validate_onAccept='SET .%s?forced_null=false;' %k, **kw)
            fb.checkbox(value='^.%s?force_null' %k,label='!!Set NULL')
            fb.checkbox(value='^.%s?replace' %k,label='!!Replace')
        box.data('.do_trigger',do_trigger)



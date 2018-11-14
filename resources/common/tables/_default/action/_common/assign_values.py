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
        batchflags= self.batch_parameters.get('batchflags')
        do_trigger = self.batch_parameters.get('do_trigger')
        self.tblobj

        def isBoolCol(col):
            return self.tblobj.column(col).dtype=='B'

        def updater(row):
            for k,v in values.items():
                f=batchflags[k]
                if row[k] is not None and not f['replace']:
                    return
                if f['forced_null']:
                    row[k] = None
                    return
                if v is None and isBoolCol(k):
                    v=False
                row[k] = v
                
        self.batchUpdate(updater,_raw_update=not do_trigger,message='setting_values')
        self.db.commit()


    def table_script_parameters_pane(self, pane, table=None,**kwargs):
        tblobj = self.db.table(table)
        do_trigger = False
        box = pane.div(max_height='600px',overflow='auto')
        fb = box.formbuilder(margin='5px',cols=3,border_spacing='3px',dbtable=table)
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
            fb.field(k,validate_notnull=False,html_label=True,zoom=False,lbl_fieldname=k, datapath='.values',
                        validate_onAccept='SET .#parent.batchflags.%s.forced_null=false;' %k, **kw)
            fb.checkbox(value='^.%s.forced_null' %k , datapath='.batchflags',label='SET NULL', validate_onAccept="""if(userChange && value){
                SET .%s = null;
            }""" %k)
            fb.checkbox(value='^.%s.replace' %k,label='!!Replace', datapath='.batchflags')
        box.data('.do_trigger',do_trigger)



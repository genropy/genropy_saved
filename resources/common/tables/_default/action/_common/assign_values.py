# -*- coding: utf-8 -*-

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
        do_trigger = self.batch_parameters.get('do_trigger')
        def updater(row):
            for k,data in list(values.items()):
                if row[k] is not None and not data['replace']:
                    continue
                if data['forced_null']:
                    row[k] = None
                    continue
                v = data['value']
                if v is None and data['dtype']=='B':
                    v=False
                row[k] = v
        self.batchUpdate(updater,_raw_update=not do_trigger,message='setting_values')
        self.db.commit()


    def table_script_parameters_pane(self, pane, table=None,**kwargs):
        tblobj = self.db.table(table)
        do_trigger = False
        box = pane.div(max_height='600px',overflow='auto')
        fb = box.formbuilder(margin='5px',cols=3,border_spacing='3px',dbtable=table,datapath='.values')
        for k,v in list(tblobj.columns.items()):
            attr = v.attributes
            batch_assign = attr.get('batch_assign')
            if not batch_assign:
                continue
            kw = {}
            if batch_assign is not True:
                kw.update(batch_assign)
            if not self.application.checkResourcePermission(kw.pop('tags',None),self.userTags):
                continue
            do_trigger = kw.pop('do_trigger',False) or do_trigger
            replace = kw.get('replace',None)
            mandatory = kw.get('mandatory',False)
            fb.field(k,value='^.value',validate_notnull=False,html_label=True,zoom=False,lbl_fieldname=k, datapath='.%s' %k,
                        validate_onAccept='if(!isNullOrBlank(value)){SET .forced_null=false;}', **kw)
            if not mandatory:
                fb.checkbox(value='^.forced_null',label='SET NULL', validate_onAccept="""if(userChange && value){
                    SET .value = null;
                }""" ,datapath='.%s' %k)
            else:
                fb.div()
            fb.data('.%s.dtype' %k,attr.get('dtype'))
            if replace is None:
                fb.checkbox(value='^.replace',label='!![en]Replace',datapath='.%s' %k)
            else:
                fb.div(datapath='.%s' %k).data('.replace',replace)
        box.data('.do_trigger',do_trigger)



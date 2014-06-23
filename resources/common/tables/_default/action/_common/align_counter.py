# -*- coding: UTF-8 -*-

# test_special_action.py
# Created by Francesco Porcari on 2010-07-02.
# Copyright (c) 2011 Softwell. All rights reserved.

from gnr.web.batch.btcaction import BaseResourceAction
caption = '!!Align counter'
tags = 'superadmin,_DEV_'
description = '!!Align counter'

class Main(BaseResourceAction):
    batch_prefix = 'acnt'
    batch_title = 'Align counter'
    batch_cancellable = False
    batch_delay = 0.5
    batch_immediate = True
    
    def do(self):
        counterfields = self.batch_parameters['counterfields']
        for k,v in counterfields.items():
            to_align = v['to_align']
            if to_align:
                self.db.table('adm.counter').alignSequences(self.tblobj,field=k,to_align=to_align,thermo_wrapper=self.btc.thermo_wrapper)

        self.db.commit()

    def table_script_parameters_pane(self, pane, table=None,**kwargs):
        bc = pane.borderContainer(height='300px',width='400px')
        tblobj = self.db.table(table)
        countertable = self.db.table('adm.counter')
        fb = bc.contentPane(region='top',height='40px').formbuilder(cols=1,border_spacing='3px')
        counter_fields = tblobj.counterColumns()
        if not counter_fields:
            fb.div('!!This table has no counter field')
            return
        fb.div('!!Align counter for all records')
        tc = bc.tabContainer(region='center',margin='2px')
        for f in counter_fields:
            pane = tc.contentPane(title=f,datapath='.counterfields.%s' %f,overflow='auto',padding='10px')
            pane.checkboxText(value='^.to_align',lbl='Sq. to aling',values=','.join(countertable.getFieldSequences(tblobj,field=f)),cols=4,table_border_spacing='8px')



# -*- coding: UTF-8 -*-

# test_special_action.py
# Created by Francesco Porcari on 2010-07-02.
# Copyright (c) 2010 Softwell. All rights reserved.

from gnr.web.batch.btcprint import BaseResourcePrint

tags='user'
caption = '!!Print grid'
description='!!Print grid with template...'

class Main(BaseResourcePrint):
    batch_prefix = 'pr_rowtemplate'
    batch_cancellable = True
    batch_delay = 0.5
    batch_immediate = 'print'
    batch_title = 'Print rows'
    print_mode = 'pdf'
    html_res = 'html_res/print_gridtemplate'

    def do(self):
        selection = self.get_selection()
        if not selection:
            return
        tpl,metadata = self.db.table('adm.userobject').loadUserObject(objtype='template',
                                                                      id=self.batch_parameters['row_tpl'],
                                                                      tbl=self.tblobj.fullname)
        self.batch_parameters['grid_col_headers'] = metadata.get('description') or metadata.get('code')
        self.batch_parameters['row_tpl'] = tpl['compiled']
        self.batch_parameters['grid_row_height'] = tpl['metadata.row_height']
        virtual_columns= tpl['compiled.main?virtual_columns'] 
        self.batch_parameters['rows'] = selection.output('records',virtual_columns=virtual_columns)
        self.print_record(record='*',storagekey='x')
        
    def table_script_parameters_pane(self,pane,extra_parameters=None,record_count=None,table=None,**kwargs):
        pkg,tbl= table.split('.')
        pane = pane.div(padding='10px',min_height='60px')        
        fb = pane.formbuilder(cols=1,fld_width='20em',border_spacing='4px')
        fb.dbSelect(value='^.row_tpl', lbl='!!Row template',dbtable='adm.userobject',condition='$tbl=:mt AND $objtype=:ot AND $flags ILIKE :f',
                        condition_mt=table,condition_ot='template',condition_f='%%is_row%%',hasDownArrow=True)
        fb.dbSelect(dbtable='adm.htmltemplate', value='^.letterhead_id',lbl='!!Letterhead',hasDownArrow=True)

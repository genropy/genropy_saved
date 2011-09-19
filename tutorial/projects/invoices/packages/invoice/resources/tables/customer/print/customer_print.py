# -*- coding: UTF-8 -*-

# customer_print.py
# Created by Filippo Astolfi on 2011-09-16.
# Copyright (c) 2011 Softwell. All rights reserved.

from gnr.web.batch.btcprint import BaseResourcePrint

caption = 'Performances Print'
tags = 'user'
description = 'Performaces print'

class Main(BaseResourcePrint):
    batch_prefix = 'perf_print'
    batch_title = 'Performances Print'
    batch_delay = 0.5
    html_res = 'html_builder/customer_print'
      
    def table_script_parameters_pane(self,pane,**kwargs):
        fb = pane.formbuilder(cols=2)
        self.periodCombo(fb,lbl='!!Periodo',period_store='.period')
        fb.div(value='^.period.period_string', _class='period',font_size='.9em',font_style='italic')
        fb.dataFormula(".period_input", "'questo mese'")
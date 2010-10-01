# -*- coding: UTF-8 -*-

# test_special_action.py
# Created by Francesco Porcari on 2010-07-02.
# Copyright (c) 2010 Softwell. All rights reserved.

from gnr.web.gnrbaseclasses import BaseResourceAction
import time

caption = 'Localita belle'
tags = 'user'
description='Script che stampa le localita belle'

class Main(BaseResourceAction):
    batch_prefix = 'AP'
    batch_title = 'Localita belle'
    batch_cancellable = False
    batch_delay = 0.5
    
    def do(self):
        selection = self.get_selection()
        for loc in self.btc.thermo_wrapper(selection,'loc'):
            print '%s %s' %(loc['nome'],self.batch_parameters['pars']['test'])
            time.sleep(0.1)
        
    def result_handler(self):
        return 'Execution completed',dict(url='http://www.apple.com')
    
    def parameters_pane(self,pane,**kwargs):
        fb = pane.formbuilder(cols=2, border_spacing='3px')
        #self.periodCombo(fb,period_store='.period')
        fb.textbox(value='^.test',lbl='Test')

# -*- coding: UTF-8 -*-

# th_office.py
# Created by Francesco Porcari on 2011-04-10.
# Copyright (c) 2011 Softwell. All rights reserved.

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method
class View(BaseComponent):
    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('code',width='5em')
        r.fieldcell('direction',width='15em')
        r.fieldcell('description',width='12em')
        
    def th_order(self):
        return 'code'
        
    def th_query(self):
        return dict(column='code',op='contains',val='',runOnStart=True)
        
class Form(BaseComponent):
    def th_form(self,form):
        pane = form.record
        fb = pane.formbuilder(cols=1,border_spacing='4px')
        fb.field('child_code')
        fb.field('description')
        fb.field('account_id')
    
    def th_options(self):
        return dict(height='130px',width='200px')
        
    @public_method
    def th_onLoading(self,record,newrecord,loadingParameters,recInfo):
        if newrecord:
            if record['parent_code']:
                record['account_id'] = record['@parent_code.account_id']
        
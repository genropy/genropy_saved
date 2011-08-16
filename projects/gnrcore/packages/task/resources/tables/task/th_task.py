# -*- coding: UTF-8 -*-

# base.py
# Created by Saverio Porcari on 2011-03-13.
# Copyright (c) 2011 Softwell. All rights reserved.

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method

class View(BaseComponent):
    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('task_name',width='6em') # char(4)
        r.fieldcell('table_name',width='6em')
        r.fieldcell('command',width='6em')
        r.fieldcell('month',width='4em')
        r.fieldcell('day',width='4em')
        r.fieldcell('weekday',width='4em')
        r.fieldcell('hour',width='4em')
        r.fieldcell('minute',width='4em')
        r.fieldcell('parameters',width='4em') # date
        r.fieldcell('last_execution',width='4em')

    def th_order(self):
        return 'task_name'
        
    def th_query(self):
        return dict(column='task_name',op='contains', val='%',runOnStart=True)

    def th_options(self):
        return dict(widget='dialog',dialog_height='360px',dialog_width='600px',dialog_title='Task')

        
class Form(BaseComponent):
    
    def th_form(self, form):
        pane = form.record
        fb = pane.formbuilder(cols=2,border_spacing='4px',margin_top='10px')
        fb.field('task_name')
        fb.field('table_name')
        fb.field('command')
        fb.field('month')
        fb.field('day')
        fb.field('weekday')
        fb.field('hour')
        fb.field('minute')
        
        
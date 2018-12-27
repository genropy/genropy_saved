#!/usr/bin/python
# -*- coding: utf-8 -*-

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method

class View(BaseComponent):

    def th_struct(self,struct):
        r = struct.view().rows()
        #r.fieldcell('task_id')
        r.fieldcell('start_time',name='Start',width='10em')
        r.fieldcell('end_time',name='End',width='10em')
        r.fieldcell('is_error',name='!!Error',width='5em')
        r.fieldcell('result',name='Result',width='100%')

    def th_order(self):
        return 'start_time'

    def th_query(self):
        return dict(column='__ins_ts', op='equal', val='')



class Form(BaseComponent):

    def th_form(self, form):
        pane = form.record
        fb = pane.formbuilder(cols=2, border_spacing='4px')
        fb.field('task_id')
        fb.field('result')
        fb.field('result_time')
        fb.field('is_error')


    def th_options(self):
        return dict(dialog_height='400px', dialog_width='600px')

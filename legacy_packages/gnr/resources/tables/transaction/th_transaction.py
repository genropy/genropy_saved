#!/usr/bin/python
# -*- coding: UTF-8 -*-

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method

class View(BaseComponent):

    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('request')
        r.fieldcell('execution_start')
        r.fieldcell('execution_end')
        r.fieldcell('mode')
        r.fieldcell('action')
        r.fieldcell('implementor')
        r.fieldcell('maintable')
        r.fieldcell('data')
        r.fieldcell('error_id')
        r.fieldcell('request_id')
        r.fieldcell('request_ts')
        r.fieldcell('user_id')
        r.fieldcell('session_id')
        r.fieldcell('user_ip')
        r.fieldcell('file_name')
        r.fieldcell('queue_id')

    def th_order(self):
        return 'request'

    def th_query(self):
        return dict(column='request', op='contains', val='%')



class Form(BaseComponent):

    def th_form(self, form):
        pane = form.record
        fb = pane.formbuilder(cols=2, border_spacing='4px')
        fb.field('request')
        fb.field('execution_start')
        fb.field('execution_end')
        fb.field('mode')
        fb.field('action')
        fb.field('implementor')
        fb.field('maintable')
        fb.field('data')
        fb.field('error_id')
        fb.field('request_id')
        fb.field('request_ts')
        fb.field('user_id')
        fb.field('session_id')
        fb.field('user_ip')
        fb.field('file_name')
        fb.field('queue_id')


    def th_options(self):
        return dict(dialog_height='400px', dialog_width='600px')

#!/usr/bin/python
# -*- coding: utf-8 -*-

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method

class View(BaseComponent):

    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('tbl')
        r.fieldcell('description')
        r.fieldcell('data')
        r.fieldcell('write_ts')
        r.fieldcell('errors')
        r.fieldcell('errors_ts')
        r.fieldcell('send_ts')

    def th_order(self):
        return 'tbl'

    def th_query(self):
        return dict(column='tbl', op='contains', val='')



class Form(BaseComponent):

    def th_form(self, form):
        pane = form.record
        fb = pane.formbuilder(cols=2, border_spacing='4px')
        fb.field('tbl')
        fb.field('description')
        fb.field('data')
        fb.field('write_ts')
        fb.field('errors')
        fb.field('errors_ts')
        fb.field('send_ts')


    def th_options(self):
        return dict(dialog_height='400px', dialog_width='600px')

#!/usr/bin/python
# -*- coding: UTF-8 -*-

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method

class View(BaseComponent):

    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('user_id')
        r.fieldcell('annotation_id')
        r.fieldcell('confirm_ts')
        r.fieldcell('note')

    def th_order(self):
        return 'user_id'

    def th_query(self):
        return dict(column='user_id', op='contains', val='')



class Form(BaseComponent):

    def th_form(self, form):
        pane = form.record
        fb = pane.formbuilder(cols=2, border_spacing='4px')
        fb.field('user_id')
        fb.field('annotation_id')
        fb.field('confirm_ts')
        fb.field('note')


    def th_options(self):
        return dict(dialog_height='400px', dialog_width='600px')

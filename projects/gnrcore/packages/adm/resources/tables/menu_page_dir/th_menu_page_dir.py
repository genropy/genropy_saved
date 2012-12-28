#!/usr/bin/python
# -*- coding: UTF-8 -*-

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method

class View(BaseComponent):

    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('_row_count')
        r.fieldcell('dir_id')
        r.fieldcell('page_id')
        r.fieldcell('label')
        r.fieldcell('tags')

    def th_order(self):
        return '_row_count'

    def th_query(self):
        return dict(column='_row_count', op='contains', val='%')



class Form(BaseComponent):

    def th_form(self, form):
        pane = form.record
        fb = pane.formbuilder(cols=2, border_spacing='4px')
        fb.field('_row_count')
        fb.field('dir_id')
        fb.field('page_id')
        fb.field('label')
        fb.field('tags')


    def th_options(self):
        return dict(dialog_height='400px', dialog_width='600px')

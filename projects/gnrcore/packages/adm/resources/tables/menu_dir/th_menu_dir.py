#!/usr/bin/python
# -*- coding: UTF-8 -*-

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method

class View(BaseComponent):

    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('parent_id')
        r.fieldcell('label')
        r.fieldcell('hierarchical_label')
        r.fieldcell('_parent_h_label')
        r.fieldcell('hierarchical_pkey')
        r.fieldcell('_parent_h_pkey')
        r.fieldcell('_h_count')
        r.fieldcell('_parent_h_count')
        r.fieldcell('_row_count')
        r.fieldcell('tags')
        r.fieldcell('summary')

    def th_order(self):
        return 'parent_id'

    def th_query(self):
        return dict(column='parent_id', op='contains', val='%')



class Form(BaseComponent):

    def th_form(self, form):
        pane = form.record
        fb = pane.formbuilder(cols=2, border_spacing='4px')
        fb.field('parent_id')
        fb.field('label')
        fb.field('hierarchical_label')
        fb.field('_parent_h_label')
        fb.field('hierarchical_pkey')
        fb.field('_parent_h_pkey')
        fb.field('_h_count')
        fb.field('_parent_h_count')
        fb.field('_row_count')
        fb.field('tags')
        fb.field('summary')


    def th_options(self):
        return dict(dialog_height='400px', dialog_width='600px')

#!/usr/bin/python
# -*- coding: UTF-8 -*-

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method

class View(BaseComponent):

    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('code')
        r.fieldcell('label')
        r.fieldcell('basepath')
        r.fieldcell('tags')
        r.fieldcell('file')
        r.fieldcell('description')
        r.fieldcell('parameters')
        r.fieldcell('position')
        r.fieldcell('_class')
        r.fieldcell('_style')

    def th_order(self):
        return 'code'

    def th_query(self):
        return dict(column='code', op='contains', val='%')



class Form(BaseComponent):

    def th_form(self, form):
        pane = form.record
        fb = pane.formbuilder(cols=2, border_spacing='4px')
        fb.field('code')
        fb.field('label')
        fb.field('basepath')
        fb.field('tags')
        fb.field('file')
        fb.field('description')
        fb.field('parameters')
        fb.field('position')
        fb.field('_class')
        fb.field('_style')


    def th_options(self):
        return dict(dialog_height='400px', dialog_width='600px')

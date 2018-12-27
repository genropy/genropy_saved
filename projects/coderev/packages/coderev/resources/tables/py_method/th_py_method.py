#!/usr/bin/python
# -*- coding: utf-8 -*-

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method

class View(BaseComponent):

    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('name')
        r.fieldcell('py_module_id')
        r.fieldcell('py_class_id')
        r.fieldcell('private')
        r.fieldcell('docline')

    def th_order(self):
        return 'name'

    def th_query(self):
        return dict(column='name', op='contains', val='')



class Form(BaseComponent):

    def th_form(self, form):
        pane = form.record
        fb = pane.formbuilder(cols=2, border_spacing='4px')
        fb.field('name')
        fb.field('py_module_id')
        fb.field('py_class_id')
        fb.field('private')
        fb.field('docline')


    def th_options(self):
        return dict(dialog_height='400px', dialog_width='600px')

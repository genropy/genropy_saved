#!/usr/bin/python
# -*- coding: UTF-8 -*-

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method

class View(BaseComponent):

    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('label')
        r.fieldcell('filepath')
        r.fieldcell('dbtable')
        r.fieldcell('metadata')

    def th_order(self):
        return 'label'

    def th_query(self):
        return dict(column='label', op='contains', val='%')

class Form(BaseComponent):

    def th_form(self, form):
        pane = form.record
        fb = pane.formbuilder(cols=2, border_spacing='4px')
        fb.field('label')
        fb.field('filepath')
        fb.field('dbtable')
        fb.textbox(value='^metadata.formResource',lbl='FormResource')
        fb.textbox(value='^metadata.viewResource',lbl='ViewResource')


    def th_options(self):
        return dict(dialog_height='400px', dialog_width='600px')

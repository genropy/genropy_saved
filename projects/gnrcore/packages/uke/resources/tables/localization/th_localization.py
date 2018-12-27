#!/usr/bin/python
# -*- coding: utf-8 -*-

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method

class View(BaseComponent):

    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('package_identifier')
        r.fieldcell('localization_key')
        r.fieldcell('localization_values')

    def th_order(self):
        return 'package_identifier'

    def th_query(self):
        return dict(column='package_identifier', op='contains', val='')



class Form(BaseComponent):

    def th_form(self, form):
        pane = form.record
        fb = pane.formbuilder(cols=2, border_spacing='4px')
        fb.field('package_identifier')
        fb.field('localization_key')
        fb.field('localization_values')


    def th_options(self):
        return dict(dialog_height='400px', dialog_width='600px')

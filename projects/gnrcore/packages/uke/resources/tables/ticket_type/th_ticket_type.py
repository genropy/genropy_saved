#!/usr/bin/python
# -*- coding: UTF-8 -*-

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method

class View(BaseComponent):

    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('df_fields')
        r.fieldcell('df_fbcolumns')
        r.fieldcell('df_custom_templates')
        r.fieldcell('df_colswith')
        r.fieldcell('code')
        r.fieldcell('description')

    def th_order(self):
        return 'df_fields'

    def th_query(self):
        return dict(column='df_fields', op='contains', val='')



class Form(BaseComponent):

    def th_form(self, form):
        pane = form.record
        fb = pane.formbuilder(cols=2, border_spacing='4px')
        fb.field('df_fields')
        fb.field('df_fbcolumns')
        fb.field('df_custom_templates')
        fb.field('df_colswith')
        fb.field('code')
        fb.field('description')


    def th_options(self):
        return dict(dialog_height='400px', dialog_width='600px')

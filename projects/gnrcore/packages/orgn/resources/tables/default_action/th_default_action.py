#!/usr/bin/python
# -*- coding: UTF-8 -*-

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method

class ViewFromAnnotationType(BaseComponent):

    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('action_type_id',width='100%')

    def th_order(self):
        return 'annotation_type_id'

    def th_query(self):
        return dict(column='annotation_type_id', op='contains', val='')



class Form(BaseComponent):

    def th_form(self, form):
        pane = form.record
        fb = pane.formbuilder(cols=2, border_spacing='4px')
        fb.field('annotation_type_id')
        fb.field('action_type_id')


    def th_options(self):
        return dict(dialog_height='400px', dialog_width='600px')

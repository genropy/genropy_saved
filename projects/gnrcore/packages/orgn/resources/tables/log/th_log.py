#!/usr/bin/python
# -*- coding: UTF-8 -*-

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method

class View(BaseComponent):

    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('description')
        r.fieldcell('user_id')
        r.fieldcell('log_type_id')
        r.fieldcell('date')
        r.fieldcell('time')

    def th_order(self):
        return 'description'

    def th_query(self):
        return dict(column='description', op='contains', val='')

class ViewFromUser(BaseComponent):
    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('description')
        r.fieldcell('log_type_id')
        r.fieldcell('date')
        r.fieldcell('time')

    def th_order(self):
        return 'description'

    def th_query(self):
        return dict(column='description', op='contains', val='')



class Form(BaseComponent):

    def th_form(self, form):
        pane = form.record
        fb = pane.formbuilder(cols=2, border_spacing='4px')
        fb.field('description')
        fb.field('log_type_id')
        fb.field('date')
        fb.field('time')


    def th_options(self):
        return dict(dialog_height='400px', dialog_width='600px')


#!/usr/bin/python
# -*- coding: UTF-8 -*-

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method

class View(BaseComponent):

    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('tablename')
        r.fieldcell('tag')
        r.fieldcell('description')

    def th_order(self):
        return 'tablename'

    def th_query(self):
        return dict(column='tablename', op='contains', val='')



class Form(BaseComponent):

    def th_form(self, form):
        pane = form.record
        fb = pane.formbuilder(cols=2, border_spacing='4px')
        fb.field('tablename')
        fb.field('tag')
        fb.field('description')


    def th_options(self):
        return dict(dialog_height='400px', dialog_width='600px')

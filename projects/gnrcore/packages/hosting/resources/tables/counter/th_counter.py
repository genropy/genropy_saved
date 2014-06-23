#!/usr/bin/python
# -*- coding: UTF-8 -*-

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method

class View(BaseComponent):

    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('codekey')
        r.fieldcell('code')
        r.fieldcell('pkg')
        r.fieldcell('name')
        r.fieldcell('counter')
        r.fieldcell('last_used')
        r.fieldcell('holes')

    def th_order(self):
        return 'codekey'

    def th_query(self):
        return dict(column='codekey', op='contains', val='')



class Form(BaseComponent):

    def th_form(self, form):
        pane = form.record
        fb = pane.formbuilder(cols=2, border_spacing='4px')
        fb.field('codekey')
        fb.field('code')
        fb.field('pkg')
        fb.field('name')
        fb.field('counter')
        fb.field('last_used')
        fb.field('holes')


    def th_options(self):
        return dict(dialog_height='400px', dialog_width='600px')

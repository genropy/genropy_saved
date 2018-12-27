#!/usr/bin/python
# -*- coding: utf-8 -*-

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method

class View(BaseComponent):

    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('topic')
        r.fieldcell('type')
        r.fieldcell('identifier')
        r.fieldcell('tip')
        r.fieldcell('help')
        r.fieldcell('localizations')

    def th_order(self):
        return 'topic'

    def th_query(self):
        return dict(column='topic', op='contains', val='')



class Form(BaseComponent):

    def th_form(self, form):
        pane = form.record
        fb = pane.formbuilder(cols=2, border_spacing='4px')
        fb.field('topic')
        fb.field('type')
        fb.field('identifier')
        fb.field('tip')
        fb.field('help')
        fb.field('localizations')


    def th_options(self):
        return dict(dialog_height='400px', dialog_width='600px')

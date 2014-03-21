#!/usr/bin/python
# -*- coding: UTF-8 -*-

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method

class View(BaseComponent):

    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('code')
        r.fieldcell('name')
        r.fieldcell('code3')
        r.fieldcell('nmbr')
        r.fieldcell('nmbrunico')

    def th_order(self):
        return 'code'

    def th_query(self):
        return dict(column='code', op='contains', val='')



class Form(BaseComponent):

    def th_form(self, form):
        pane = form.record
        fb = pane.formbuilder(cols=2, border_spacing='4px')
        fb.field('code')
        fb.field('name')
        fb.field('code3')
        fb.field('nmbr')
        fb.field('nmbrunico')


    def th_options(self):
        return dict(dialog_height='400px', dialog_width='600px')

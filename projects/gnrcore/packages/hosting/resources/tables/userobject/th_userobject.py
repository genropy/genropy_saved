#!/usr/bin/python
# -*- coding: UTF-8 -*-

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method

class View(BaseComponent):

    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('code')
        r.fieldcell('objtype')
        r.fieldcell('pkg')
        r.fieldcell('tbl')
        r.fieldcell('userid')
        r.fieldcell('description')
        r.fieldcell('notes')
        r.fieldcell('data')
        r.fieldcell('authtags')
        r.fieldcell('private')
        r.fieldcell('quicklist')
        r.fieldcell('flags')

    def th_order(self):
        return 'code'

    def th_query(self):
        return dict(column='code', op='contains', val='')



class Form(BaseComponent):

    def th_form(self, form):
        pane = form.record
        fb = pane.formbuilder(cols=2, border_spacing='4px')
        fb.field('code')
        fb.field('objtype')
        fb.field('pkg')
        fb.field('tbl')
        fb.field('userid')
        fb.field('description')
        fb.field('notes')
        fb.field('data')
        fb.field('authtags')
        fb.field('private')
        fb.field('quicklist')
        fb.field('flags')


    def th_options(self):
        return dict(dialog_height='400px', dialog_width='600px')

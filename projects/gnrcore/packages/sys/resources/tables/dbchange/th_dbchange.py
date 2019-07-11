#!/usr/bin/python
# -*- coding: utf-8 -*-

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method

class View(BaseComponent):

    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('ref')
        r.fieldcell('tbl')
        r.fieldcell('record_pkey')
        r.fieldcell('evt')
        r.fieldcell('record')
        r.fieldcell('dbstore')

    def th_order(self):
        return 'ref'

    def th_query(self):
        return dict(column='ref', op='contains', val='')



class Form(BaseComponent):

    def th_form(self, form):
        pane = form.record
        fb = pane.formbuilder(cols=2, border_spacing='4px')
        fb.field('ref')
        fb.field('tbl')
        fb.field('record_pkey')
        fb.field('evt')
        fb.field('record')
        fb.field('dbstore')


    def th_options(self):
        return dict(dialog_height='400px', dialog_width='600px')

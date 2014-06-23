#!/usr/bin/python
# -*- coding: UTF-8 -*-

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method

class View(BaseComponent):

    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('tablename')
        r.fieldcell('event')
        r.fieldcell('username')
        r.fieldcell('record_pkey')
        r.fieldcell('version')
        r.fieldcell('data')
        r.fieldcell('transaction_id')

    def th_order(self):
        return 'tablename'

    def th_query(self):
        return dict(column='tablename', op='contains', val='')



class Form(BaseComponent):

    def th_form(self, form):
        pane = form.record
        fb = pane.formbuilder(cols=2, border_spacing='4px')
        fb.field('tablename')
        fb.field('event')
        fb.field('username')
        fb.field('record_pkey')
        fb.field('version')
        fb.field('data')
        fb.field('transaction_id')


    def th_options(self):
        return dict(dialog_height='400px', dialog_width='600px')

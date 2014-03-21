#!/usr/bin/python
# -*- coding: UTF-8 -*-

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method

class View(BaseComponent):

    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('transaction_id')
        r.fieldcell('request')
        r.fieldcell('client')
        r.fieldcell('action')
        r.fieldcell('maintable')
        r.fieldcell('data')

    def th_order(self):
        return 'transaction_id'

    def th_query(self):
        return dict(column='transaction_id', op='contains', val='')



class Form(BaseComponent):

    def th_form(self, form):
        pane = form.record
        fb = pane.formbuilder(cols=2, border_spacing='4px')
        fb.field('transaction_id')
        fb.field('request')
        fb.field('client')
        fb.field('action')
        fb.field('maintable')
        fb.field('data')


    def th_options(self):
        return dict(dialog_height='400px', dialog_width='600px')

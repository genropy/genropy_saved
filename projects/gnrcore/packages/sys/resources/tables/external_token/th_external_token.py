#!/usr/bin/python
# -*- coding: UTF-8 -*-

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method

class View(BaseComponent):

    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('datetime')
        r.fieldcell('expiry')
        r.fieldcell('allowed_user')
        r.fieldcell('connection_id')
        r.fieldcell('max_usages')
        r.fieldcell('allowed_host')
        r.fieldcell('page_path')
        r.fieldcell('method')
        r.fieldcell('parameters')
        r.fieldcell('exec_user')

    def th_order(self):
        return 'datetime'

    def th_query(self):
        return dict(column='datetime', op='contains', val='')



class Form(BaseComponent):

    def th_form(self, form):
        pane = form.record
        fb = pane.formbuilder(cols=2, border_spacing='4px')
        fb.field('datetime')
        fb.field('expiry')
        fb.field('allowed_user')
        fb.field('connection_id')
        fb.field('max_usages')
        fb.field('allowed_host')
        fb.field('page_path')
        fb.field('method')
        fb.field('parameters')
        fb.field('exec_user')


    def th_options(self):
        return dict(dialog_height='400px', dialog_width='600px')

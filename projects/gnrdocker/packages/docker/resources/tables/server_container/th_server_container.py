#!/usr/bin/python3
# -*- coding: utf-8 -*-

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method

class View(BaseComponent):

    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('container_id')
        r.fieldcell('server_id')

    def th_order(self):
        return 'container_id'

    def th_query(self):
        return dict(column='container_id', op='contains', val='')



class Form(BaseComponent):

    def th_form(self, form):
        pane = form.record
        fb = pane.formbuilder(cols=2, border_spacing='4px')
        fb.field('container_id')
        fb.field('server_id')


    def th_options(self):
        return dict(dialog_height='400px', dialog_width='600px')

#!/usr/bin/python
# -*- coding: utf-8 -*-

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method

class View(BaseComponent):

    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('sync_utc')
        r.fieldcell('sync_origin_db')
        r.fieldcell('sync_table')
        r.fieldcell('sync_pkey')
        r.fieldcell('sync_event')
        r.fieldcell('sync_data')

    def th_order(self):
        return 'sync_utc'

    def th_query(self):
        return dict(column='sync_utc', op='contains', val='')



class Form(BaseComponent):

    def th_form(self, form):
        pane = form.record
        fb = pane.formbuilder(cols=2, border_spacing='4px')
        fb.field('sync_utc')
        fb.field('sync_origin_db')
        fb.field('sync_table')
        fb.field('sync_pkey')
        fb.field('sync_event')
        fb.field('sync_data')


    def th_options(self):
        return dict(dialog_height='400px', dialog_width='600px')

#!/usr/bin/python
# -*- coding: utf-8 -*-

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method

class View(BaseComponent):

    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('tablename')
        r.fieldcell('event_type')
        r.fieldcell('event_pkey')
        r.fieldcell('event_data')
        r.fieldcell('event_check_ts')
        r.fieldcell('status')
        r.fieldcell('topic')
        r.fieldcell('author')
        r.fieldcell('server_user')
        r.fieldcell('server_ts')

    def th_order(self):
        return 'tablename'

    def th_query(self):
        return dict(column='tablename', op='contains', val='')



class Form(BaseComponent):

    def th_form(self, form):
        pane = form.record
        fb = pane.formbuilder(cols=2, border_spacing='4px')
        fb.field('tablename')
        fb.field('event_type')
        fb.field('event_pkey')
        fb.field('event_data')
        fb.field('event_check_ts')
        fb.field('status')
        fb.field('topic')
        fb.field('author')
        fb.field('server_user')
        fb.field('server_ts')


    def th_options(self):
        return dict(dialog_height='400px', dialog_width='600px')

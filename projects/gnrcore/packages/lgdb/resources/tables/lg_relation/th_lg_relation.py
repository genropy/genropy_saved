#!/usr/bin/python3
# -*- coding: utf-8 -*-

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method

class View(BaseComponent):

    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('rel_name', width='8em')
        r.fieldcell('relation_column',  width='15em')
        r.fieldcell('related_column', width='15em')
        r.fieldcell('rel_mode')
        r.fieldcell('rel_on_delete', width='8em',)

    def th_order(self):
        return 'relation_column'

    def th_query(self):
        return dict(column='relation_column', op='contains', val='')


class Form(BaseComponent):

    def th_form(self, form):
        pane = form.record
        pass


    def th_options(self):
        return dict(dialog_height='400px', dialog_width='600px' )

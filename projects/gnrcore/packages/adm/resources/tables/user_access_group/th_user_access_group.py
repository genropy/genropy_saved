#!/usr/bin/python
# -*- coding: utf-8 -*-

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method

class View(BaseComponent):

    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('user_id')
        r.fieldcell('access_group_code')

    def th_order(self):
        return 'user_id'

    def th_query(self):
        return dict(column='user_id', op='contains', val='')

class ViewFromAccessGroup(BaseComponent):

    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('user_id')

    def th_order(self):
        return 'user_id'

class ViewFromAccessUser(BaseComponent):

    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('access_group_code')

    def th_order(self):
        return 'access_group_code'


class Form(BaseComponent):

    def th_form(self, form):
        pane = form.record
        fb = pane.formbuilder(cols=2, border_spacing='4px')
        fb.field('user_id')
        fb.field('access_group_code')


    def th_options(self):
        return dict(dialog_height='400px', dialog_width='600px')

#!/usr/bin/python
# -*- coding: UTF-8 -*-

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method

class View(BaseComponent):

    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('code')
        r.fieldcell('description')
      

    def th_order(self):
        return 'code'

    def th_query(self):
        return dict(column='code', op='contains', val='')


class Form(BaseComponent):

    def th_form(self, form):
        bc = form.center.borderContainer()
        top_pane= bc.contentPane(region='top', datapath='.record')
        fb = top_pane.formbuilder(cols=2, border_spacing='4px')
        fb.field('code')
        fb.field('description')
        center_pane= bc.contentPane(region='center').dialogTableHandler(relation='@hosts')

    def th_options(self):
        return dict(dialog_windowRatio=.9)
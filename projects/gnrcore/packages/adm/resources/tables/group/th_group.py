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
        return '_row_count'

    def th_query(self):
        return dict(column='description', op='contains', val='')



class Form(BaseComponent):

    def th_form(self, form):
        bc = form.center.borderContainer()
        fb = bc.contentPane(region='top',datapath='.record').formbuilder(cols=2, border_spacing='4px')
        fb.field('code')
        fb.field('description')
        bc.contentPane(region='center').plainTableHandler(relation='@users')


    def th_options(self):
        return dict(dialog_height='400px', dialog_width='600px')

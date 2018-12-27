#!/usr/bin/python
# -*- coding: utf-8 -*-

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method

class View(BaseComponent):

    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('name')
        r.fieldcell('description')

    def th_order(self):
        return 'name'

    def th_query(self):
        return dict(column='name', op='contains', val='')



class Form(BaseComponent):

    def th_form(self, form):
        bc = form.center.borderContainer()
        fb = bc.contentPane(region='top',datapath='.record').formbuilder(cols=2, border_spacing='4px')
        fb.field('name')
        fb.field('description')
        tc = bc.tabContainer(region='center')
        tc.contentPane(title='Projects').dialogTableHandler(relation='@projects',viewResource='ViewFromCustomer',formResource='FormFromCustomer')
        tc.contentPane(title='People').dialogTableHandler(relation='@people',viewResource='ViewFromCustomer',formResource='FormFromCustomer')



    def th_options(self):
        return dict(dialog_height='400px', dialog_width='600px')

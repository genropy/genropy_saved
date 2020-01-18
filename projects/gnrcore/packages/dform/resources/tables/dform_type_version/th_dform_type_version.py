#!/usr/bin/python
# -*- coding: utf-8 -*-

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method

class View(BaseComponent):

    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('dform_type_id')
        r.fieldcell('version_code')
        r.fieldcell('date_from')
        r.fieldcell('date_to')

    def th_order(self):
        return 'date_from'

    def th_query(self):
        return dict(column='dform_type_id', op='contains', val='')



class Form(BaseComponent):

    def th_form(self, form):
        bc = form.center.borderContainer()
        fb = bc.contentPane(region='top',datapath='.record').formbuilder(cols=2, border_spacing='4px')
        fb.field('dform_type_id')
        fb.field('version_code',validate_notnull=True,validate_case='u')
        fb.field('date_from')
        fb.field('date_to')
        bc.contentPane(region='center').dialogTableHandler(relation='@data_elements')


    def th_options(self):
        return dict(dialog_height='400px', dialog_width='600px')

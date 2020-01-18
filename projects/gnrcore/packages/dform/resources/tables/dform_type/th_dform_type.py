#!/usr/bin/python
# -*- coding: utf-8 -*-

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method

class View(BaseComponent):
    def th_hiddencolumns(self):
        return "$_row_count"

    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('hierarchical_name')
        r.fieldcell('description')

    def th_order(self):
        return '_row_count'

    def th_query(self):
        return dict(column='hierarchical_name', op='contains', val='')



class Form(BaseComponent):

    def th_form(self, form):
        bc = form.center.borderContainer()
        top = bc.contentPane(region='top',datapath='.record')
        fb = top.formbuilder(cols=3, border_spacing='4px')
        fb.field('code',validate_case='u')
        fb.field('name')
        fb.field('description')
        tc = bc.tabContainer(region='center',margin='2px')
        self.dataElements(tc.contentPane(title='!![en]Elements'))
    
    def dataElements(self,pane):
        pane.dialogTableHandler(relation='@versions')


    def th_options(self):
        return dict(dialog_height='400px', dialog_width='600px',hierarchical=True)

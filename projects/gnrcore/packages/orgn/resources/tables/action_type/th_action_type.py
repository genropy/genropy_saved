#!/usr/bin/python
# -*- coding: UTF-8 -*-

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method

class View(BaseComponent):

    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('hierarchical_name')

    def th_order(self):
        return 'hierarchical_name'

    def th_query(self):
        return dict(column='hierarchical_name', op='contains', val='')



class Form(BaseComponent):
    py_requires='gnrcomponents/dynamicform/dynamicform:DynamicForm'

    def th_form(self, form):
        bc = form.center.borderContainer()
        top = bc.contentPane(region='top',datapath='.record')
        fb = top.formbuilder(cols=3, border_spacing='4px')
        fb.field('name')
        fb.field('default_priority')
        fb.field('default_days_before')
        bc.contentPane(region='center').fieldsGrid(title='Fields',pbl_classes=True,margin='2px')


    def th_options(self):
        return dict(dialog_height='400px', dialog_width='600px',hierarchical=True)

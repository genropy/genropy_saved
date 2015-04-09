#!/usr/bin/python
# -*- coding: UTF-8 -*-

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method

class View(BaseComponent):

    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('hierarchical_name')
        r.fieldcell('summary')

    def th_order(self):
        return 'hierarchical_name'

    def th_query(self):
        return dict(column='hierarchical_name', op='contains', val='')



class Form(BaseComponent):
    py_requires ="""gnrcomponents/dynamicform/dynamicform:DynamicForm"""

    def th_form(self, form):
        bc = form.center.borderContainer()
        fb = bc.contentPane(region='top',datapath='.record').div(margin_right='10px').formbuilder(cols=3, border_spacing='4px',fld_width='100%',width='100%',colswidth='auto')
        fb.field('name',colspan=2)
        fb.field('server',html_label=True)
        fb.field('summary',tag='simpleTextArea',colspan=3,height='100px')

        bc.contentPane(region='center').fieldsGrid(margin='2px',rounded=6,border='1px solid silver') #ok


    def th_options(self):
        return dict(dialog_height='400px', dialog_width='600px',hierarchical=True,duplicate=True)

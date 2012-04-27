# -*- coding: UTF-8 -*-

# base.py
# Created by Francesco Porcari on 2011-03-13.
# Copyright (c) 2011 Softwell. All rights reserved.

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method

class View(BaseComponent):
    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('name',width='100%')

    def th_order(self):
        return 'name'
        
    def th_query(self):
        return dict(column='name',op='contains', val='%',runOnStart=True)
    def th_options(self):
        return dict()
        
class Form(BaseComponent):
    py_requires='gnrcomponents/dynamicform/dynamicform:DynamicForm'
    def th_form(self, form):
        bc = form.center.borderContainer()
        top = bc.contentPane(region='top',datapath='.record')
        fb = top.formbuilder(cols=2)
        fb.field('name')
        fb.field('example_link')
        
        tc=bc.tabContainer(region='center')
        tc.contentPane(title='Description')
        tc.contentPane(title='Parameters').fieldsGrid(title='!!Characteristics')
        tc.contentPane(title='Examples')
        
        
        

    def th_options(self):
        return dict(hierarchical='open')
        
class FormTest(BaseComponent):
    def th_options(self):
        return dict(hierarchical='open')
        
    def th_form(self, form):
        bc = form.center.borderContainer()
        top = bc.contentPane(region='top',datapath='.record')
        fb = top.formbuilder(cols=2)
        fb.field('name')

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
    py_requires='gnrcomponents/dynamicform/dynamicform:DynamicForm,foundation/macrowidgets:RichTextEditor'
    def th_form(self, form):
        bc = form.center.borderContainer()
        top = bc.contentPane(region='top',datapath='.record')
        fb = top.formbuilder(cols=1)
        fb.field('name')
        fb.field('example_link',width='50em')
        
        tc=bc.tabContainer(region='center',margin='2px',margin_left='4px')
        self.RichTextEditor(tc.contentPane(title='Description'),value='^#FORM.record.long_description')
        tc.contentPane(title='Parameters').fieldsGrid(title='!!Characteristics',pbl_classes=True,margin='2px')
        tc.contentPane(title='Examples',overflow='hidden').iframe(src='^#FORM.record.example_link',height='100%',width='100%',border=0)

    def th_options(self):
        return dict(hierarchical='open')


        

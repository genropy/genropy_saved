#!/usr/bin/python
# -*- coding: UTF-8 -*-

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method

class View(BaseComponent):

    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('name')
        r.fieldcell('code')
        r.fieldcell('restrictions')

    def th_order(self):
        return 'name'

    def th_query(self):
        return dict(column='name', op='contains', val='')



class Form(BaseComponent):
    py_requires='gnrcomponents/dynamicform/dynamicform:DynamicForm'

    def th_form(self, form):
        bc = form.center.borderContainer()
        top = bc.contentPane(region='top',datapath='.record')
        fb = top.formbuilder(cols=4, border_spacing='4px')
        fb.field('name')
        fb.field('code')
        restrictions = self.db.table('orgn.annotation').getRestrictions()
        if restrictions:
            fb.field('restrictions',tag='checkBoxText',values=restrictions,popup=True,cols=1)
        bc.contentPane(region='center').fieldsGrid(title='Fields',pbl_classes=True,margin='2px')


    def th_options(self):
        return dict(dialog_height='400px', dialog_width='600px')

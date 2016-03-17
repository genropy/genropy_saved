#!/usr/bin/python
# -*- coding: UTF-8 -*-

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method

class View(BaseComponent):

    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('code',width='5em')
        r.fieldcell('description',width='15em')
        r.fieldcell('extended_description',width='20em')
        r.fieldcell('restrictions',width='10em')

    def th_order(self):
        return 'description'

    def th_query(self):
        return dict(column='description', op='contains', val='')



class Form(BaseComponent):
    py_requires='gnrcomponents/dynamicform/dynamicform:DynamicForm'

    def th_form(self, form):
        bc = form.center.borderContainer()
        top = bc.contentPane(region='top',datapath='.record')
        fb = top.formbuilder(cols=1, border_spacing='4px')
        fb.field('code')
        fb.field('description')
        fb.field('default_priority')
        fb.field('default_days_before')
        fb.field('extended_description',tag='simpleTextArea',lbl='Extended description')
        fb.field('default_tag',condition='$child_count = 0 AND $isreserved IS NOT TRUE',
                tag='dbselect',
                dbtable='adm.htag',alternatePkey='code',hasDownArrow=True)
        restrictions = self.db.table('orgn.annotation').getRestrictions()
        if restrictions:
            fb.field('restrictions',tag='checkBoxText',values=restrictions,popup=True,cols=1)
        bc.contentPane(region='center').fieldsGrid(title='Fields',pbl_classes=True,margin='2px')


    def th_options(self):
        return dict(dialog_height='400px', dialog_width='600px')

#!/usr/bin/python
# -*- coding: UTF-8 -*-

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method

class View(BaseComponent):

    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('title',width='16em')
        r.fieldcell('year',width='4em')
        r.fieldcell('actor',width='16em')
        r.fieldcell('character',width='16em')      
        r.fieldcell('role',width='12em')
        r.fieldcell('note')
        r.fieldcell('nr_order')
        
    def th_options(self):
        return dict(tableRecordCount=False)
        
    def th_order(self):
        return 'actor'

    def th_query(self):
        return dict(column='title', op='startswith', val='')



class Form(BaseComponent):

    def th_form(self, form):
        pane = form.record
        fb = pane.formbuilder(cols=2, border_spacing='4px')
        fb.field('person_id')
        fb.field('movie_id')
        fb.field('person_role_id')
        fb.field('note')
        fb.field('nr_order')
        fb.field('role_id')


    def th_options(self):
        return dict(dialog_height='400px', dialog_width='600px')

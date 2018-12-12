#!/usr/bin/python
# -*- coding: utf-8 -*-

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method

class View(BaseComponent):

    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('person_id')
        r.fieldcell('public_key')

    def th_order(self):
        return 'person_id'

    def th_query(self):
        return dict(column='person_id', op='contains', val='')



class ViewFromPerson(BaseComponent):

    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('__ins_ts',hidden=True)
        r.fieldcell('public_key',width='100%',edit=dict(tag='simpleTextArea'))

    def th_order(self):
        return '__ins_ts'


class Form(BaseComponent):

    def th_form(self, form):
        pane = form.record
        fb = pane.formbuilder(cols=2, border_spacing='4px')
        fb.field('person_id')
        fb.field('public_key')


    def th_options(self):
        return dict(dialog_height='400px', dialog_width='600px')

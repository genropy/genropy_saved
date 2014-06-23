#!/usr/bin/python
# -*- coding: UTF-8 -*-

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method

class View(BaseComponent):

    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('code')
        r.fieldcell('slot_type')
        r.fieldcell('used')
        r.fieldcell('instance_id')

    def th_order(self):
        return 'code'

    def th_query(self):
        return dict(column='code', op='contains', val='')


class ViewFromInstance(BaseComponent):

    def th_struct(self,struct):
        r = struct.view().rows()
        #r.fieldcell('code',edit=True)
        r.fieldcell('slot_type_id',edit=dict(hasDownArrow=True))
        r.fieldcell('quantity',edit=True,width='5em')
    def th_order(self):
        return 'code'

    def th_query(self):
        return dict(column='code', op='contains', val='')



class Form(BaseComponent):

    def th_form(self, form):
        pane = form.record
        fb = pane.formbuilder(cols=2, border_spacing='4px')
        fb.field('code')
        fb.field('slot_type')
        fb.field('used')
        fb.field('instance_id')


    def th_options(self):
        return dict(dialog_height='400px', dialog_width='600px')

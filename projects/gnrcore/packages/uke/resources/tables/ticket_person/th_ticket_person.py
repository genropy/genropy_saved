#!/usr/bin/python3
# -*- coding: utf-8 -*-

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method

class ViewFromTicket(BaseComponent):

    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('person_id',edit=True,width='15em')
        r.fieldcell('role',edit=True)

    def th_order(self):
        return 'person_id'

    def th_query(self):
        return dict(column='person_id', op='contains', val='')



class Form(BaseComponent):

    def th_form(self, form):
        pane = form.record
        fb = pane.formbuilder(cols=2, border_spacing='4px')
        fb.field('person_id')
        fb.field('ticket_id')
        fb.field('role')


    def th_options(self):
        return dict(dialog_height='400px', dialog_width='600px')

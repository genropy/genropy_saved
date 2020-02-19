#!/usr/bin/python3
# -*- coding: utf-8 -*-

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method

class View(BaseComponent):

    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('lg_table_id')
        r.fieldcell('name', width='8em')
        r.fieldcell('data_type', name='T', width='3em')
        r.fieldcell('description', width='15em', edit=True)
        r.fieldcell('notes', width='40em', edit=dict(tag='simpleTextArea', height='80px'))
        r.fieldcell('group', width='8em', edit=True)

    def th_order(self):
        return 'lg_table_id'

    def th_query(self):
        return dict(column='name', op='contains', val='')




class Form(BaseComponent):

    def th_form(self, form):
        pane = form.record
        fb = pane.div(margin_right='10px').formbuilder(cols=2, border_spacing='4px', width='100%', fld_width='100%')
        fb.field('lg_table_id' )
        fb.field('name' )
        fb.field('data_type')
        fb.field('group')
        fb.field('description', colspan=2 )
        fb.field('notes', tag='simpleTextArea', height='90px')

    def th_options(self):
        return dict(dialog_height='400px', dialog_width='600px' )

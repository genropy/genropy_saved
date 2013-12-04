#!/usr/bin/python
# -*- coding: UTF-8 -*-

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method

class View(BaseComponent):

    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('__ins_ts',name='Datetime')
        r.fieldcell('error_type')

        r.fieldcell('description')
        r.fieldcell('username')
        r.fieldcell('user_ip')
        r.fieldcell('user_agent')
        r.fieldcell('fixed')
        r.fieldcell('notes')

    def th_order(self):
        return 'description'

    def th_query(self):
        return dict(column='description', op='contains', val='%')

    def th_bottom_custom(self,bar):
        bar.slotToolbar('sections@error_type,*')

    def th_sections_error_type(self):
        return [dict(code='exc',caption='!!Exceptions',condition="$error_type=:c",condition_c='EXC'),
                dict(code='err',caption='!!Errors',condition="$error_type=:c",condition_c='ERR')]


class Form(BaseComponent):

    def th_form(self, form):
        pane = form.record
        fb = pane.formbuilder(cols=2, border_spacing='4px')
        fb.field('error_type')
        fb.field('description')
        fb.field('username')
        fb.field('user_ip')
        fb.field('user_agent',colspan=2)
        fb.field('error_data',colspan=2)


    def th_options(self):
        return dict(dialog_height='400px', dialog_width='600px')

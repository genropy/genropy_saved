#!/usr/bin/python
# -*- coding: utf-8 -*-

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method

class View(BaseComponent):

    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('page_id')
        r.fieldcell('pagename')
        r.fieldcell('connection_id')
        r.fieldcell('start_ts')
        r.fieldcell('end_ts')
        r.fieldcell('end_reason')

    def th_order(self):
        return 'page_id'

    def th_query(self):
        return dict(column='page_id', op='contains', val='')


    def th_bottom_custom(self,bottom):
        bottom.slotToolbar('sections@isopen,*')

    def th_sections_isopen(self):
        return [dict(code='open',caption='!!Open',condition="$end_ts IS NULL"),
                dict(code='closed',caption='!!Closed',condition="$end_ts IS NOT NULL"),
                dict(code='all',caption='!!All')]

class ViewFromConnection(View):

    def th_top_custom(self,top):
        top.bar.replaceSlots('vtitle','sections@isopen')


    def th_bottom_custom(self,bar):
        pass

class Form(BaseComponent):

    def th_form(self, form):
        pane = form.record
        fb = pane.formbuilder(cols=2, border_spacing='4px')
        fb.field('page_id')
        fb.field('pagename')
        fb.field('connection_id')
        fb.field('start_ts')
        fb.field('end_ts')
        fb.field('end_reason')


    def th_options(self):
        return dict(dialog_height='400px', dialog_width='600px')

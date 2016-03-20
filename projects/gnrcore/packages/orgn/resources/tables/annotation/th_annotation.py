#!/usr/bin/python
# -*- coding: UTF-8 -*-

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method

class View(BaseComponent):

    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('annotation_caption')
        r.fieldcell('description')
        #r.fieldcell('log_id')

    def th_order(self):
        return 'annotation_caption'

    def th_query(self):
        return dict(column='annotation_caption', op='contains', val='')

class ViewAction(BaseComponent):

    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('annotation_caption')
        r.fieldcell('assigned_to')
        r.fieldcell('priority',width='6em')
        r.fieldcell('days_before')
        #r.fieldcell('log_id')

    def th_order(self):
        return 'annotation_caption'

    def th_query(self):
        return dict(column='annotation_caption', op='contains', val='')

class ViewPlugin(View):
    def th_hiddencolumns(self):
        return '$connected_fkey'

    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('template_cell',width='100%', name='-')
        #r.fieldcell('__ins_ts',name='Ins')
        #r.fieldcell('annotation_caption')
        #r.fieldcell('priority')
        #r.fieldcell('connected_description',name='Connected to')

    def th_top_custom(self,top):
        top.bar.replaceSlots('#','*,sections@priority,*')

    def th_options(self):
        return dict(liveUpdate=True)
        
    def th_order(self):
        return '$__ins_ts'

class Form(BaseComponent):
    def th_form(self, form):
        form.record



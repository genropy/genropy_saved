#!/usr/bin/python
# -*- coding: utf-8 -*-

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method,metadata

class View(BaseComponent):

    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('__ins_ts',width='10em')

        r.fieldcell('task_id')
        r.fieldcell('@task_id.table_name')
        r.fieldcell('@task_id.command')
        r.fieldcell('pid')
        r.fieldcell('start_ts')
        r.fieldcell('end_ts')
        r.fieldcell('is_error')
        r.fieldcell('status')

    def th_order(self):
        return '__ins_ts:d'



    def th_query(self):
        return dict(column='task_id', op='contains', val='')

class ViewFromTask(BaseComponent):

    def th_order(self):
        return '__ins_ts:d'

    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('__ins_ts',width='10em')
        r.fieldcell('pid')
        r.fieldcell('start_ts',width='10em')
        r.fieldcell('end_ts',width='10em')
        r.fieldcell('result',width='8em')
        r.fieldcell('is_error',width='5em',name='Error')
        r.fieldcell('status')

    def th_top_custom(self,top):
        top.bar.replaceSlots('vtitle','sections@secstat')
    
    @metadata(multiButton=True)
    def th_sections_secstat(self):
        return [
            dict(code='active',condition="$status IN :st",condition_st=['running','waiting'],caption='Active'),
            dict(code='completed',condition="$status=:st",condition_st='completed',caption='Completed'),
            dict(code='error',condition="$status=:st",condition_st='error',caption='Error')
        ]


class Form(BaseComponent):

    def th_form(self, form):
        pane = form.record
        fb = pane.formbuilder(cols=2, border_spacing='4px')
        fb.field('task_id')
        fb.field('result')
        fb.field('pid')
        fb.field('start_ts')
        fb.field('end_ts')
        fb.field('is_error')


    def th_options(self):
        return dict(dialog_height='400px', dialog_width='600px')

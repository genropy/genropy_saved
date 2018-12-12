#!/usr/bin/python
# -*- coding: utf-8 -*-

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method

class View(BaseComponent):

    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('action_type_id')
        r.fieldcell('outcome_action_type_id')

    def th_order(self):
        return 'action_type_id'

    def th_query(self):
        return dict(column='action_type_id', op='contains', val='')


class ViewFromActionType(BaseComponent):

    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('_row_count',hidden=True,counter=True)
        r.fieldcell('description',edit=dict(validate_notnull=True),width='20em')
        r.fieldcell('outcome_action_type_id')
        r.fieldcell('deadline_days',edit=True)
        r.fieldcell('default_priority',edit=True,width='12em')
        r.fieldcell('default_tag',edit=dict(condition='$child_count = 0 AND $isreserved IS NOT TRUE',
                                            tag='dbselect',dbtable='adm.htag',alternatePkey='code',hasDownArrow=True),
                    width='15em')

    def th_order(self):
        return 'action_type_id'

    def th_query(self):
        return dict(column='action_type_id', op='contains', val='')



class Form(BaseComponent):

    def th_form(self, form):
        pane = form.record
        fb = pane.formbuilder(cols=2, border_spacing='4px')
        fb.field('action_type_id')
        fb.field('outcome_action_type_id')


    def th_options(self):
        return dict(dialog_height='400px', dialog_width='600px')

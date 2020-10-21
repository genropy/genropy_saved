#!/usr/bin/python
# -*- coding: utf-8 -*-

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method

class View(BaseComponent):

    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('week')
        r.fieldcell('start_date')
        r.fieldcell('end_date')

    def th_order(self):
        return 'week'

    def th_query(self):
        return dict(column='date', op='contains', val='')
    
    def th_bottom_custom(self,bottom):
        bar = bottom.slotToolbar('*,populateBtn,5')
        bar.populateBtn.slotButton('Populate',action="PUBLISH populate_week = {start_date:start_date,end_date:end_date}",ask=dict(title='Period',
                                                       fields=[dict(name='start_date',lbl='Start',wdg='dateTextBox',period_to='end_date',validate_notnull=True),
                                                              dict(name='end_date',lbl='End',wdg='dateTextBox',validate_notnull=True)]))
        bar.dataRpc(None,self.db.table('adm.week').populate,subscribe_populate_week=True,_lockScreen=True)


    def th_query(self):
        return dict(column='start_date', op='equal', val='')


class Form(BaseComponent):

    def th_form(self, form):
        pane = form.record
        fb = pane.formbuilder(cols=2, border_spacing='4px')
        fb.field('week')
        fb.field('start_date')
        fb.field('end_date')


    def th_options(self):
        return dict(dialog_height='400px', dialog_width='600px')

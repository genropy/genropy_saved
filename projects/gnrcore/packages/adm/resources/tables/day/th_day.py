#!/usr/bin/python
# -*- coding: utf-8 -*-

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method

class View(BaseComponent):

    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('date')
        r.fieldcell('weekday')
        r.fieldcell('is_holyday')

    def th_order(self):
        return 'date'

    def th_query(self):
        return dict(column='date', op='contains', val='')
    
    def th_bottom_custom(self,bottom):
        bar = bottom.slotToolbar('*,populateBtn,5')
        bar.populateBtn.slotButton('Populate',action="PUBLISH populate_days = {date_start:date_start,date_end:date_end}",ask=dict(title='Period',
                                                       fields=[dict(name='date_start',lbl='Date start',wdg='dateTextBox',period_to='date_end',validate_notnull=True),
                                                              dict(name='date_end',lbl='Date end',wdg='dateTextBox',validate_notnull=True)]))
        bar.dataRpc(None,self.db.table('adm.day').populate,subscribe_populate_days=True,_lockScreen=True)



class Form(BaseComponent):

    def th_form(self, form):
        pane = form.record
        fb = pane.formbuilder(cols=2, border_spacing='4px')
        fb.field('date')
        fb.field('weekday')
        fb.field('is_holyday')


    def th_options(self):
        return dict(dialog_height='400px', dialog_width='600px')

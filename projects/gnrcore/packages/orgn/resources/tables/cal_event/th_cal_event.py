#!/usr/bin/python
# -*- coding: utf-8 -*-

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method

class View(BaseComponent):

    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('description')
        r.fieldcell('dtstart')
        r.fieldcell('dtend')

    def th_order(self):
        return 'description'

    def th_query(self):
        return dict(column='description', op='contains', val='')



class Form(BaseComponent):

    def th_form(self, form):
        pane = form.record
        fb = pane.formbuilder(cols=2, border_spacing='4px')
        fb.field('description',colspan=2,validate_notnull=True,width='100%')
        fb.dateTextBox(value='^.date_start',validate_notnull=True,
                        width='7em',lbl='!![en]Start date')
        fb.dateTextBox(value='^.time_start',validate_notnull=True,
                        width='7em',lbl='!![en]Time')
        fb.dateTextBox(value='^.date_end',validate_notnull=True,
                        width='7em',lbl='!![en]End date')
        fb.dateTextBox(value='^.time_end',validate_notnull=True,
                        width='7em',lbl='!![en]Time')
        fb.geoCoderField(value='^.geodesc',
                        lbl='!![en]Location',selected_position='.geocode')

    def th_onLoading(self, record, newrecord, loadingParameters, recInfo):
        dtstart,dtend = record['dtstart'],dtend
        if dtstart:
            record['date_start'] = dtstart.date()
            record['time_start'] = dtstart.time()
        if dtend:
            record['date_end'] = dtend.date()
            record['time_end'] = dtend.time()


    def th_options(self):
        return dict(dialog_height='400px', dialog_width='600px')

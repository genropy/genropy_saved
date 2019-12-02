#!/usr/bin/python
# -*- coding: utf-8 -*-

from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrdecorator import public_method
import datetime
import pytz


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
        bc = form.center.borderContainer()
        fb = bc.contentPane(region='top',datapath='.record').formbuilder(cols=2, 
                        border_spacing='4px')
        fb.field('description',colspan=2,validate_notnull=True,width='100%')
        fb.dateTextBox(value='^.date_start',validate_notnull=True,
                        width='7em',lbl='!![en]Start date')
        fb.timeTextBox(value='^.time_start',validate_notnull=True,
                        width='7em',lbl='!![en]Hour/Min')
        fb.dateTextBox(value='^.date_end',validate_notnull=True,
                        width='7em',lbl='!![en]End date')
        fb.timeTextBox(value='^.time_end',validate_notnull=True,
                        width='7em',lbl='!![en]Hour/Min')
        fb.geoCoderField(value='^.geodesc',
                        lbl='!![en]Location',
                        colspan=2,width='100%',
                        selected_position='.geocoder')
        bc.contentPane(region='center',border_top='1px solid silver').GoogleMap(height='100%',
                     map_center="^#FORM.record.geocoder",
                     map_type='roadmap',
                     map_zoom=15,
                     centerMarker=True,
                     map_disableDefaultUI=True)
        
    @public_method
    def th_onLoading(self, record, newrecord, loadingParameters, recInfo):
        dtstart,dtend = record['dtstart'],record['dtend']
        if dtstart:
            record.setItem('date_start', dtstart.date(),_sendback=True)
            record.setItem('time_start',dtstart.time(),_sendback=True)
        if dtend:
            record.setItem('date_end', dtend.date(),_sendback=True)
            record.setItem('time_end',dtend.time(),_sendback=True)
    
    @public_method
    def th_onSaving(self, recordCluster,recordClusterAttr, resultAttr=None):
        recordCluster['dtstart'] = datetime.datetime(recordCluster['date_start'].year,
                                recordCluster['date_start'].month,
                                recordCluster['date_start'].day,
                                recordCluster['time_start'].hour,
                                recordCluster['time_start'].minute)
        recordCluster['dtend'] = datetime.datetime(recordCluster['date_end'].year,
                                recordCluster['date_end'].month,
                                recordCluster['date_end'].day,
                                recordCluster['time_end'].hour,
                                recordCluster['time_end'].minute)


    def th_options(self):
        return dict(dialog_height='400px', dialog_width='400px')

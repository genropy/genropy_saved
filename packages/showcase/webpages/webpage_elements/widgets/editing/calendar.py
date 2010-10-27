#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-
#
#  untitled
#
#  Created by Giovanni Porcari on 2007-03-24.
#  Copyright (c) 2007 Softwell. All rights reserved.
#

""" GnrDojo Hello World """
import os

import datetime
from gnr.core.gnrbag import Bag, DirectoryResolver

class GnrCustomWebPage(object):
    py_requires='public:Public'
    css_requires='calendar'
    js_requires='Calendar'
    def main(self, root, **kwargs):
        cp=root.borderContainer(region='top',**kwargs)
        root.data('aux.calevents',self.myEvents())
        root.calendar(width='800px',height='400px',storepath='aux.calevents')
        dialog= cp.borderContainer(region= 'center')
        root.dataRpc('aux.calevents', 'getNewEvent', _fired='^updateEvent', _init=False)
        #cp.button('Update', fire='updateEvent', margin='20px')
        root.button('Update', fire='aux.newCalendarEventDialog.show', margin='20px')
        root.data('aux.newCalendarEventDialog', Bag())
        root.dataController("""
                        var record = genro.getData('aux.newCalendarEventDialog');
                        var date = record.getItem('date');
                        var start_hour = record.getItem('start_time');
                        var end_hour = record.getItem('end_time');
                        var s=new Date(date);
                        s.setHours(start_hour.getHours(),start_hour.getMinutes());
                        var e=new Date(date);
                        e.setHours(end_hour.getHours(),end_hour.getMinutes());
                        var calendar_event= new Object();
                        var id = genro.getCounter();
                        calendar_event.start_time=s;
                        calendar_event.end_time=e;
                        calendar_event.id=id;
                        calendar_event.date=date;
                        calendar_event.title=record.getItem('title');
                        calendar_event.event_type='meeting';
                        calendar_event.description=record.getItem('description');
                        var calevents=genro.getData('aux.calevents');
                        calevents.setItem(calendar_event.id,null,calendar_event,null);
                        """,_fired="^aux.newCalendarEventDialog.create")
        newEventDialog = self.hiddenTooltipDialog(dialog, dlgId='newCalendarEventDialog', title="!!New event creation",
                        width="42em",height="23ex",fired='^aux.newCalendarEventDialog.show', 
                        datapath='aux.newCalendarEventDialog',
                        bottom_right='!!Insert',bottom_right_action='FIRE aux.newCalendarEventDialog.create;FIRE aux.newCalendarEventDialog.close')
        dlgpane = newEventDialog.contentPane(region='center',_class='pbl_dialog_center')
        dlgformbuilder=dlgpane.formbuilder(cols=4, border_spacing='4px')
        dlgformbuilder.textbox(lbl='Title',value='^.title',width='5em')
        dlgformbuilder.textbox(lbl='Description',value='^.description',width='5em')
        dlgformbuilder.datetextbox(lbl='Date', value='^.date', dtype='D',width='5em')
        dlgformbuilder.timetextbox(lbl='Start at', value='^.start_time', dtype='DH',width='5em')
        dlgformbuilder.timetextbox(lbl='End at', value='^.end_time', dtype='DH',width='5em')

    def myEvents(self):
        b=Bag()
        b.setItem('id3',None,{
            'id': 'id3',
            'date':'2008-12-27::D',
            'start_time': "2008-12-27 14:00:00::DH",
            'end_time': "2008-12-27 15:00:00::DH",
            'all_day': False,
            'repeated': False,
            'title': "Title 3",
            'description': "This is the body of entry with id: id3 and title: Title 3",
            'event_type': "reminder,meeting"})
        return b

    def rpc_getNewEvent(self):
        b=Bag()
        b.setItem('id2',None,{
            'id': 'id2',
            'date':'2008-12-26::D',
            'start_time': "2008-12-26 13:00:00::DH",
            'end_time': "2008-12-26 15:00:00::DH",
            'all_day': False,
            'repeated': False,
            'title': "Title 2",
            'description': "This is the body of entry with id: id3 and title: Title 3",
            'event_type': "reminder,meeting"})
        b.setItem("2008-12-27",None,{
            'id': 'id4',
            'date':"2008-12-27::D",
            'start_time': "2008-12-27 16:00:00::DH",
            'end_time': "2008-12-27 17:00:00::DH",
            'all_day': False,
            'repeated': False,
            'title': "Title 4",
            'description': "This is the body of entry with id: id3 and title: Title 3",
            'event_type': "reminder,meeting"})
        return b


# -*- coding: utf-8 -*-
# 
"""fullcalendar_base"""

class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerFull"
    def test_1_base(self, pane):
        """Basic button"""
        kw = {'initialView':'dayGridMonth',
              'headerToolbar': {
                    'center': 'addEventButton'
              },
            'customButtons': {
                'addEventButton': {
                'text': 'add event...'}
        }}
        pane.fullCalendar(box_margin='40px',box_max_width='1100px',**kw)

    def test_2_event_store(self, pane):
        bc = pane.borderContainer(height='900px')
        bc.contentPane(region='center').fullCalendar(initialView='dayGridMonth',     
        headerToolbar={
            'left': 'dayGridMonth,timeGridWeek,listWeek,timeGridDay',
            'center': 'title',
            'right': 'prevYear,prev,next,nextYear'
        },box_margin='40px',box_max_width='1100px',storepath='.events')


        bottom = bc.borderContainer(region='bottom',height='300px',splitter=True)
        grid = bottom.contentPane(region='center').quickGrid(value='^.events')
        grid.tools('delrow,addrow')
        grid.column('event_id',edit=True,name='Event',width='15em')
        grid.column('title',edit=True,name='title',width='15em')
        grid.column('start_date',edit=dict(tag='dateTextBox',period_to='.end_date'),dtype='D',name='start date',width='10em')
        grid.column('start_time',edit=dict(tag='timeTextBox'),name='time',width='10em',dtype='H')
        grid.column('end_date',edit=dict(tag='dateTextBox'),name='end date',width='10em',dtype='D')
        grid.column('end_time',edit=dict(tag='timeTextBox'),name='time',width='10em',dtype='H')
        grid.column('start',formula="combineDateAndTime(start_date,start_time)",name='Start',dtype='DHZ')
        grid.column('end',formula="combineDateAndTime(end_date,end_time)",name='End',dtype='DHZ')

        footer = bottom.contentPane(region='bottom')
        footer.button('Set',fire='.set')
  
    def test_3_event_store(self, pane):
        bc = pane.borderContainer(height='900px')
        bc.contentPane(region='center').fullCalendar(initialView='dayGridMonth',     
        headerToolbar={
            'left': 'dayGridMonth,timeGridWeek,listWeek,timeGridDay',
            'center': 'title',
            'right': 'prevYear,prev,next,nextYear'
        },box_margin='40px',box_max_width='1100px')

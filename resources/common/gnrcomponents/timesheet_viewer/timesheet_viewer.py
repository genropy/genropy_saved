# -*- coding: utf-8 -*-

from gnr.web.gnrbaseclasses import BaseComponent

from gnr.core.gnrdecorator import public_method
from gnr.web.gnrwebstruct import struct_method


class TimesheetViewer(BaseComponent):
    css_requires = 'gnrcomponents/timesheet_viewer/timesheet_viewer'
    js_requires = 'gnrcomponents/timesheet_viewer/timesheet_viewer,chroma.min'

    @struct_method
    def ts_timesheetViewer(self,parent,value=None,date_start=None,date_end=None,
                            selected_date=None,
                            work_start=None,work_end=None,slotFiller=None,slot_duration=None,
                            minute_height=None,
                            viewerMode=None,**kwargs):
        if viewerMode is None:
            viewerMode = 'stackCalendar'
        selected_date = selected_date or self.workdate
        if viewerMode=='stackCalendar':
            frame = self.ts_stackCalendarViewer(parent,selected_date=selected_date,**kwargs)
        elif viewerMode=='singleDay':
            frame = self.ts_singleDayViewer(parent,selected_date=selected_date,**kwargs)

        parent.dataController("""
                            date_start = date_start || selected_date;
                            date_end = date_end || addDaysToDate(date_start,90);
                            if(!frame.viewerController){
                                frame.viewerController = new gnr.TimesheetViewerController(frame,{
                                                                                 frameCode:frame.attr.frameCode,
                                                                                 date_start:date_start,
                                                                                 date_end:date_end,
                                                                                 work_start:work_start,
                                                                                 work_end:work_end,
                                                                                 slotFiller:slotFiller,
                                                                                 slot_duration:slot_duration,
                                                                                 minute_height:minute_height});
                            }
                            frame.viewerController.setData(data);
                            if(viewerMode=='stackCalendar'){
                                frame.viewerController.showMonthly();
                                frame.setRelativeData('.lastRebuilt',new Date());
                            }else if(viewerMode=='singleDay'){
                                frame.viewerController.fillFullDay(selected_date);
                            }
                           """,
                           selected_date = selected_date,
                           date_start=date_start,
                           date_end = date_end,slotFiller=slotFiller,
                           work_end=work_end,work_start=work_start,slot_duration=slot_duration,
                           data=value,frame=frame,viewerMode=viewerMode,minute_height=minute_height)

        frame.dataController("""if(viewerPage=='calendarViewer' && lastRebuilt){
            SET .lastRebuilt = null;
            frame.viewerController.refresh();
        }
        
        """,viewerPage='^.viewerPage',lastRebuilt='=.lastRebuilt',frame=frame)

        #root.dataController("FIRE reloadslots;",doctor_id='^current.doctor_id',_delay=100)
        #root.onDbChanges("""if(window.slotsviewer){
        #        window.slotsviewer.onEventChange(dbChanges);
        #    }""", table='base.event')
        return frame
                                                                            


    def ts_singleDayViewer(self,pane,frameCode=None,
                    datapath=None,selected_date=None,**kwargs):
        if not frameCode:
            frameCode = 'timesheet_viewer'
        daypage_nodeId = '%s_day_viewer' %frameCode
        daypage = pane.framePane(frameCode=frameCode,
                                datapath=datapath,_anchor=True,
                                **kwargs)
        selected_date = selected_date or self.workdate
        daybar = daypage.top.slotToolbar('*,refresh,10')
        daybar.data('.selectedDate',selected_date)
        daybar.refresh.slotButton('!!Refesh',iconClass='iconbox arrow_circle_right',action='FIRE #ANCHOR.refresh;')
        daypage.center.contentPane(nodeId=daypage_nodeId,_class='dayview')
        return daypage



    def ts_stackCalendarViewer(self,pane,frameCode=None,
                    datapath=None,selected_date=None,**kwargs):
        if not frameCode:
            frameCode = 'timesheet_viewer'
        daypage_nodeId = '%s_day_viewer' %frameCode
        monthpage_nodeId = '%s_month_viewer' %frameCode

        kwargs['subscribe_%s_selected' %monthpage_nodeId] = """            
            if($1.selected && this.viewerController){
                var redrawDict = this.viewerController.month_redraw || {};
                var redrawDate = objectPop(redrawDict,$1.page);
                if(redrawDate){
                    this.viewerController.rebuildMonthPage(redrawDate);
                }
            }
        """
        frame = pane.framePane(frameCode=frameCode,
                                datapath=datapath,_anchor=True,
                                connect_resize="""var that = this;
                                this.delayedCall(function(){
                                    if(that.viewerController){
                                        that.viewerController.refresh();
                                    };
                                },500,'resizing');
                                
                                """,
                                **kwargs)

        selected_date = selected_date or self.workdate
        sc = frame.center.stackContainer(selectedPage='^.viewerPage')        
        monthpage = sc.framePane(title='!!Calendar',pageName='calendarViewer')
        monthpage.top.slotToolbar('5,parentStackButtons,*,stackButtons,5',stackButtons_stackNodeId=monthpage_nodeId)
        bc = monthpage.center.borderContainer()
        bc.stackContainer(nodeId=monthpage_nodeId,selectedPage='^.selectedMonth',region='center',_class='viewcalendar')
        bc.contentPane(region='bottom',height='50px')

        daypage = sc.framePane(title='!!Selected date',pageName='dayViewer')
        daybar = daypage.top.slotToolbar('5,parentStackButtons,*,prev,dbox,next,5,today_btn,20,refresh,10')
        daybar.prev.slotButton('Prev',iconClass='iconbox previous',
                                    action='_frame.viewerController.selectCalendarDate(addDaysToDate(date,-1));',
                                    date='=.selectedDate',_frame=frame)
        daybar.data('.selectedDate',selected_date)
        daybar.dbox.dateTextBox(value='^.selectedDate',lbl='',width='8em',validate_onAccept='if(userChange && value){window.slotsviewer.selectCalendarDate(value);}')
        daybar.next.slotButton('Next',iconClass='iconbox next',
                        action='_frame.viewerController.selectCalendarDate(addDaysToDate(date,1));',
                        date='=.selectedDate',_frame=frame)
        daybar.today_btn.slotButton('Today',action='_frame.viewerController.selectCalendarDate(wd);',wd=self.workdate,
                                    _frame=frame)
        daybar.refresh.slotButton('!!Refesh',iconClass='iconbox arrow_circle_right',action='FIRE #ANCHOR.refresh;')
        daypage.center.contentPane(nodeId=daypage_nodeId,_class='dayview')
        return frame




    #@public_method
    #def calendarFrame(self,pane,doctor_id=None,selected_date=None):
    #    if not doctor_id:
    #        pane.div('!!Select a DOCTOR from the top right menu',font_weight='bold',color='#003366',margin='1.5em')
    #        return
    #    if  self.isMobile:
    #        return self.calendarFrameMobile(pane,doctor_id=doctor_id,selected_date=selected_date)
#
    #    frame = pane.framePane(frameCode='calendar')
    #    bar = frame.top.slotToolbar('5,stackButtons,*,prev,dbox,next,5,today_btn,20,refresh,5',stackButtons_stackNodeId='month_viewer')
    #    rbar = frame.right.slotToolbar('30,zoombar,*')
    #    bar.prev.slotButton('Prev',iconClass='iconbox previous',action='window.slotsviewer.selectCalendarDate(addDaysToDate(date,-1));',date='=.selectedDate')
    #    selected_date = selected_date or self.workdate
    #    bar.data('.selectedDate',selected_date)
    #    bar.dbox.dateTextBox(value='^.selectedDate',lbl='',width='8em',validate_onAccept='if(userChange && value){window.slotsviewer.selectCalendarDate(value);}')
    #    bar.next.slotButton('Next',iconClass='iconbox next',action='window.slotsviewer.selectCalendarDate(addDaysToDate(date,1));',date='=.selectedDate')
    #    bar.today_btn.slotButton('Today',action='window.slotsviewer.selectCalendarDate(wd);',wd=self.workdate)
    #    bar.refresh.slotButton('Refesh dashboard',iconClass='iconbox arrow_circle_right',action='FIRE reloadslots;')
#
    #    rbar.zoombar.verticalSlider(value='^.scale_y',lbl='Scale',height='18em',minimum=.5, maximum=4,
    #                        intermediateChanges=True)
    #    bar.dataController("""var sv = window.slotsviewer;
    #                        if(sv.scale_y==scale_y){
    #                            return;
    #                        }
    #                        sv.scale_y = scale_y;
    #                        sv.fillFullDay(selectedDate);
    #                        """,scale_y='^.scale_y',selectedDate='=.selectedDate')
    #    bc = frame.center.borderContainer()
    #    bc.data('.selectedMonth',selected_date)
    #    left = bc.borderContainer(width='690px',region='left',splitter=True)
    #    left.contentPane(region='bottom',height='40px').div(position='absolute',top='5px',left=0,right=0,
    #                                                        text_align='center').div('^current.doctor_record.name_full',font_size='15pt',
    #                                                                                    color='white',padding='2px',padding_left='12px',
    #                                                                                    padding_right='12px',rounded=10,background='#666',display='inline-block')
    #    left.stackContainer(nodeId='month_viewer',selectedPage='^.selectedMonth',region='center')
    #    bc.contentPane(nodeId='day_viewer',region='center',border_left='1px solid silver')

# -*- coding: UTF-8 -*-
#--------------------------------------------------------------------------
# Copyright (c) : 2004 - 2007 Softwell sas - Milano 
# Written by    : Giovanni Porcari, Michele Bertoldi
#                 Saverio Porcari, Francesco Porcari , Francesco Cavazzana
#--------------------------------------------------------------------------
#This library is free software; you can redistribute it and/or
#modify it under the terms of the GNU Lesser General Public
#License as published by the Free Software Foundation; either
#version 2.1 of the License, or (at your option) any later version.

#This library is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
#Lesser General Public License for more details.

#You should have received a copy of the GNU Lesser General Public
#License along with this library; if not, write to the Free Software
#Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA

"""
Component for thermo:
"""
from gnr.web.gnrwebpage import BaseComponent
from gnr.core.gnrstring import toText

class Timetable(BaseComponent):
    py_requires='foundation/tools:RemoteBuilder'
    css_requires='public'
    def timetable_dh(self,parent,nodeId=None,datapath=None,tstart=None,
                    tstop=None,period=None,wkdlist=None,fired=None):
        assert nodeId,'nodeId is mandatory'
        assert datapath,'datapath is mandatory'
        assert hasattr(self,'tt_%s_loop'%nodeId), 'you must define your own loop'
        bc = parent.borderContainer(nodeId=nodeId,datapath=datapath,_class='pbl_roundedGroup',border='1px solid gray')
        top = bc.contentPane(region='top',background='gray',_class='pbl_roundedGroupLabel')
        bottom = bc.contentPane(region='bottom',datapath='.controller',
                                _class='pbl_roundedGroupBottom')
        bottom.horizontalSlider(value='^.zoom', minimum=.2, maximum=3,
                                intermediateChanges=True,width='15em',float='right')
        bottom.data('.zoom',1)
        center = bc.contentPane(region='center')
        self.lazyContent(center,'ttdh_main',nodeId=nodeId,tstart=tstart,tstop=tstop,period=period,wkdlist=wkdlist,fired=fired)
    
    def remote_ttdh_main(self,pane,tstart=None,tstop=None,period=None,wkdlist=None,fired=None,nodeId=None):
        
        iterator = getattr(self,'tt_%s_loop'%nodeId)
        def rect(**kwargs):
            result = dict(position='absolute')
            for k,v in kwargs.items():
                if v is not None:
                    result[k] = '%ipx' %v
            return result
        days = list(iterator(tstart=tstart,tstop=tstop,period=period,wkdlist=wkdlist))
        day_h = 50
        first_col_w = 80
        minute_w = 6
        first_margin = 3
        margin = 1
        hour_w = 60*minute_w
        start_hour = tstart.hour
        stop_hour = tstop.hour
        if tstop.minute:
            stop_hour+=1
        start_minutes = start_hour*60 
        stop_minutes = stop_hour*60 
        
        delta_minutes = (stop_hour-start_hour)*60
        tot_w = delta_minutes*minute_w
        tot_h = (len(days)+1)*day_h
        ttbox = pane.div(zoomFactor='^.controller.zoom',
                        position='relative')#,height='%ipx' %tot_h,width='%ipx' %tot_w)

        first_col = ttbox.div(**rect(left=0,top=0,width=first_col_w-first_margin,height=tot_h))
        time_col = ttbox.div(**rect(left=first_col_w,top=0))
        for hour in range(start_hour,stop_hour):
            left = (((hour-start_hour)*60)*minute_w)+first_col_w
            if hour%2:
                _class = 'hour_c1'
            else:
                _class = 'hour_c2'
            r = rect(left=left,top=0,width=hour_w-margin,height=tot_h)
            print r
            ttbox.div(border_right='1px dotted lightgray',_class=_class,**r)
        
        currline=None
        for j,dayrow in enumerate(days):
            day = dayrow['day']
            slots = dayrow['slots']
            top = j*day_h+1
            daylabel = first_col.div(_class='dayLabel',**rect(left=1,top=top,width=first_col_w-first_margin-2,height=day_h-3))
            daylabel.div(toText(day,format='eeee',locale=self.locale),_class='dayLabel_WD WD_%i' %day.weekday())
            daylabel.div(toText(day,format='d',locale=self.locale),_class='dayLabel_D')
            daylabel.div(toText(day,format='MMMM',locale=self.locale),_class='dayLabel_M')
            for slot in slots:
                left = ((slot['ts'].hour-start_hour)*60+slot['ts'].minute)*minute_w
                width = slot['minutes'] *minute_w-3
                patient =  slot['patient']
                if patient is None:
                    status = 'ttfree'
                elif patient == '-':
                    status = 'ttunavailable'
                else:
                    status = 'ttbusy'

                slotdiv = time_col.div(_class='ttslot %s' %status,**rect(left=left,top=top,width=width,height=day_h-3))
                slotdiv.div(_class='ttslot_T').span(toText(slot['ts'],format='HH:mm'),margin='5px')
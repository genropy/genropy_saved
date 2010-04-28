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
from gnr.core.gnrdate import dayIterator


def rect(**kwargs):
    result = dict(position='absolute')
    for k,v in kwargs.items():
        if v is not None:
            result[k] = '%ipx' %v
    return result

class Timetable(BaseComponent):
    py_requires='foundation/tools:RemoteBuilder'
    css_requires='public'
    def timetable_dh(self,parent,nodeId=None,datapath=None,tstart=None,
                    tstop=None,period=None,wkdlist=None,fired=None):
        assert nodeId,'nodeId is mandatory'
        assert datapath,'datapath is mandatory'
        assert hasattr(self,'tt_%s_dataProvider'%nodeId), 'you must define your own loop'
        bc = parent.borderContainer(nodeId=nodeId,datapath=datapath,_class='pbl_roundedGroup',border='1px solid gray')
        top = bc.contentPane(region='top',background='gray',_class='pbl_roundedGroupLabel')
        bottom = bc.contentPane(region='bottom',datapath='.controller',
                                _class='pbl_roundedGroupBottom')
        bottom.horizontalSlider(value='^.zoom', minimum=.2, maximum=3,
                                intermediateChanges=True,width='15em',float='right')
        bottom.data('.zoom',1)
        center = bc.contentPane(region='center')
        self.lazyContent(center,'ttdh_main',nodeId=nodeId,tstart=tstart,tstop=tstop,period=period,wkdlist=wkdlist,fired=fired)
    
    def remote_ttdh_main(self,pane,tstart=None,tstop=None,period=None,wkdlist=None,fired=None,nodeId=None,series=None):
        series=series or ['x','y']
        days = self.tt_periodSlots(tstart=tstart,tstop=tstop,period=period,wkdlist=wkdlist,series=series,nodeId=nodeId)
        day_h = 50
        sh = day_h/len(series)
        day_h=sh*len(series)
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
        tot_h = len(days)*day_h
        ttbox = pane.div(zoomFactor='^.controller.zoom',
                        position='relative')#,height='%ipx' %tot_h,width='%ipx' %tot_w)

        first_col = ttbox.div(**rect(left=0,top=0,width=first_col_w,height=tot_h))
        time_col = ttbox.div(**rect(left=first_col_w,top=0,height=tot_h,width=delta_minutes*minute_w))
        for hour in range(start_hour,stop_hour):
            left = ((hour-start_hour)*60)*minute_w
            if hour%2:
                _class = 'hour_c1'
            else:
                _class = 'hour_c2'
            r = rect(left=left,top=0,height=tot_h,width=hour_w)
            time_col.div(_class=_class,**r)
        currline=None
        for j,dayrow in enumerate(days):
            day = dayrow['day']
            series = dayrow['series']
            top = j*day_h
            daycell = first_col.div(**rect(left=0,top=top,width=first_col_w,height=day_h))
            timecell = time_col.div(z_index=100,_class='timerow',**rect(left=0,right=0,top=top,height=day_h))
            self.tt_daylabel(nodeId=nodeId,cell=daycell,day=day)
            sh = day_h/len(series)
            for ns,ks in enumerate(series.items()):
                s_top=ns*sh 
                key,slots=ks
                serierow = timecell.div(**rect(left=0,top=s_top,height=sh))
                for slot in slots:
                    left = ((slot['ts'].hour-start_hour)*60+slot['ts'].minute)*minute_w
                    width = slot['minutes'] *minute_w
                    slotcell = serierow.div(**rect(top=1,left=left+1,bottom=1,width=width-1))
                    #_class='ttslot %s' %status,
                    self.tt_slot(nodeId=nodeId,cell=slotcell,slot=slot,width=width,height=sh)

    def tt_periodSlots(self,period=None,wkdlist=None,tstart=None,tstop=None,series=None,nodeId=None):
        wkdlist = [int(k) for k,v in wkdlist.items() if v] or None
        result = []
        series = series or ['x']
        provider_handler = getattr(self,'tt_%s_dataProvider' %nodeId)
        for day in dayIterator(period,locale=self.locale,workdate=self.workdate,wkdlist=wkdlist):
            serieData = dict()
            for k in series:
                serieData[k] = provider_handler(day=day,serie=k,tstart=tstart,tstop=tstop)
            result.append(dict(series=serieData,day=day))
        return result
                
    def tt_slot(self,nodeId=None,cell=None,**kwargs):
        getattr(self,'tt_%s_slot' %nodeId)(cell,**kwargs)
        
    def tt_daylabel(self,nodeId=None,cell=None,day=None):
        if hasattr(self,'tt_%s_daylabel' %nodeId):
            return getattr(self,'tt_%s_daylabel' %nodeId)(cell,day=day)
        pane = cell.div(_class='dayLabel',**rect(top=1,bottom=1,left=1,right=1))
        pane.div(toText(day,format='eeee',locale=self.locale),_class='dayLabel_WD WD_%i' %day.weekday())
        pane.div(toText(day,format='d',locale=self.locale),_class='dayLabel_D')
        pane.div(toText(day,format='MMMM',locale=self.locale),_class='dayLabel_M')
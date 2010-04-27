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
Component for referto:
"""
import random
from datetime import date,datetime,time,timedelta
from gnr.core.gnrdate import dayIterator


class GnrCustomWebPage(object):
    py_requires='foundation/macrowidgets,gnrcomponents/timetable:Timetable'
    css_requires='public'

    def pageAuthTags(self, method=None, **kwargs):
        return ''
        
    def windowTitle(self):
         return 'Timetable'
     
    def main(self,root,**kwargs):
        bc = root.borderContainer()
        top = bc.contentPane(region='top',height='40px').toolbar()
        fb = top.formbuilder(cols=6, border_spacing='2px',datapath='top',width='100%')
        fb.data('.period.period','mese scorso')
        fb.data('.tstart',time(15,10))
        fb.data('.tstop',time(19,20))
        self.periodCombo(fb,lbl='!!Period')
        fb.timeTextBox(value='^.tstart',width='10em',lbl='!!Start')
        fb.timeTextBox(value='^.tstop',width='10em',lbl='!!Stop')
        cbgroup = fb.formbuilder(cols=7, border_spacing='2px',width='100%',colspan=2)
        cbgroup.checkbox(lbl='Sun',value='^.wkdlist.0')
        cbgroup.checkbox(lbl='Mon',value='^.wkdlist.1')
        cbgroup.checkbox(lbl='Tue',value='^.wkdlist.2')
        cbgroup.checkbox(lbl='Wed',value='^.wkdlist.3')
        cbgroup.checkbox(lbl='Thu',value='^.wkdlist.4')
        cbgroup.checkbox(lbl='Fri',value='^.wkdlist.5')
        cbgroup.checkbox(lbl='Sat',value='^.wkdlist.6')
        fb.button('Create',fire='build')
        center = bc.contentPane(region='center',margin='20px')
        self.timetable_dh(center,nodeId='mytt',datapath='test',
                        period='=top.period.period',
                        tstart='=top.tstart',tstop='=top.tstop',
                        wkdlist='=top.wkdlist',fired='^build')
        
           
    def tt_mytt_loop(self,period=None,wkdlist=None,tstart=None,tstop=None):
        wkdlist = [int(k) for k,v in wkdlist.items() if v] or None
        for day in dayIterator(period,locale=self.locale,workdate=self.workdate,wkdlist=wkdlist):
            timecurr = datetime.combine(day,tstart)
            timestop = datetime.combine(day,tstop)
            deltavisits = timedelta(minutes=(int(random.random()*3)+1)*60)
            slots = []
            while timecurr+deltavisits <= timestop:
                minutes=(int(random.random()*3)+1)*10
                deltaminutes = timedelta(minutes=minutes)
                if random.random()>.4:
                    timeslot = timecurr
                    while timeslot+deltaminutes<=timecurr+deltavisits:
                        docName = ['Verdi','Bianchi','Rossi','Neri'][int(random.random()*3)]
                        slot = dict(day=day,ts=timeslot,minutes=minutes,doctor=docName)
                        z=random.random()
                        if z<.25:
                            slot['patient'] = None
                        elif z<.9:
                            slot['patient'] = ['Morelli','Bappini','Panzarotti','Baboden','Capatonda','Fufolo'][int(random.random()*5)]
                        else:
                            slot['patient'] = '-'
                        slots.append(slot)
                        timeslot += deltaminutes
                timecurr+=deltavisits
            yield dict(slots=slots,day=day)

                
        
        
    def main_(self, root, **kwargs):
        root.data('zoomFactor',1)
        root.css('.zoommed',"""z-index:99; 
                                 -moz-transform-origin: center; 
                                 -moz-transform: scale(2);
                                 cursor:pointer;
                                 """)
        root.horizontalSlider(value='^zoomFactor', minimum=0, maximum=1,
                                intermediateChanges=True,width='15em',float='right')
        box = root.div(height='500px',width='800px',border='1px solid black',
                        overflow_x='auto',overflow_y='auto')
        inner = box.div(zoomFactor='^zoomFactor',
                        border='1px dotted navy',position='relative')
        h = 90
        w = 140
        for y in range(36):
            cy = y*100+1
            for x in range(36):
                cx = x*150+1
                if random.random() > .5:
                    disp = random.random()
                    if disp > .7:
                        color = 'green'
                    elif disp > .3:
                        color = 'red'
                    else:
                        color = 'orange'
                        
                    app = inner.div(background=color,position='absolute',top='%ipx' %cy,left='%ipx' %cx,
                            height='%ipx' %h,width='%ipx' %w,border='1px solid gray',
                            _class='rounded_max shadow_2',connect_onclick='genro.dom.setClass(this.domNode,"zoommed","toggle")')
                            
                    if disp> .3:
                        app.div('dottor pierone')
                        app.div('ore 13:22')
                        app.div('paziente mario')
        
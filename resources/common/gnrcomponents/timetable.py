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
        center = bc.contentPane(region='center')
        center.data('.zoom',1)
        inner = center.div(position='absolute',top='3px',bottom='3px',left='3px',right='3px')
        self.lazyContent(inner,'ttdh_main',nodeId=nodeId,tstart=tstart,tstop=tstop,period=period,wkdlist=wkdlist,fired=fired)
    
    def remote_ttdh_main(self,pane,tstart=None,tstop=None,period=None,wkdlist=None,fired=None,nodeId=None):
        ttbox = pane.div(zoomFactor='^.controller.zoom',
                        border='1px solid navy')
        iterator = getattr(self,'tt_%s_loop'%nodeId)
        def rect(x=None,y=None,h=None,w=None):
            return dict(left='%ipx' %x,top='%ipx' %y,height='%ipx' %h,width='%ipx' %w,position='absolute')
            
        currline=None
        for slot in iterator(tstart=tstart,tstop=tstop,period=period,wkdlist=wkdlist):
            if currline != slot['line']:
                currline = slot['line']
                top = currline*100
                daylabel = ttbox.div(background_color='pink',**rect(x=1,y=top,w=40,h=100))
                textDay = toText(slot['day'],format='DD-M-YYYY')
                daylabel.div(textDay)
    
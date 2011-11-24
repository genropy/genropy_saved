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

"""Component for thermo"""
from gnr.web.gnrbaseclasses import BaseComponent
from gnr.core.gnrstring import toText
from gnr.core.gnrdate import dayIterator
from babel import dates

def rect(**kwargs):
    result = dict(position='absolute')
    for k, v in kwargs.items():
        if v is not None:
            result[k] = '%ipx' % v
    return result

class Timetable(BaseComponent):
    py_requires = 'foundation/tools:CSSHandler'
    css_requires = 'public'

    def tt_left(self, bc, wkdlist):
        center = bc.contentPane(region='center')
        fb = center.formbuilder(cols=2, border_spacing='2px', datapath='.conf.dayrow.day')
        weekdays = dates.get_day_names(width='wide', locale=self.locale.replace('-', '_'))
        for k in wkdlist:
            fb.div(background='^.color', lbl=weekdays[k], datapath='.%i' % k, border='1px solid black',
                   baseClass='no_background',
                   height='12px', width='12px', connectedMenu='tt_colorPaletteMenu',
                   _set_background_color='.dayrow_wd%i:"#"' % k)

        fb = center.formbuilder(cols=1, border_spacing='2px', width='80%')
        fb.horizontalSlider(value='^.conf.dayrow.height', lbl='Height', minimum=50,
                            maximum=100, intermediateChanges=True, _set_height='.dayrow:#+"px"',
                            _set_font_size='.daylabel_day:#-30+"px"')

        fb.horizontalSlider(value='^.conf.labelcolumn.width', lbl='Daylabel', minimum=30,
                            maximum=100, intermediateChanges=True, _set_width='.labelcolumn:#+"px"',
                            _set_left='.contentcolumn:#+"px"')

    def tt_bottom(self, bottom, wkdlist):
        bottom.horizontalSlider(value='^.zoom', minimum=.2, maximum=3,
                                intermediateChanges=True, width='15em', float='right')
        bottom.data('.zoom', 1)
        btn = bottom.button('!!Configuration', action='SET .layoutregions.left?show=!GET .layoutregions.left?show',
                            float='left')
        fb = bottom.formbuilder(cols=7, border_spacing='2px', datapath='.conf.dayrow.day', float='left')
        weekdays = dates.get_day_names(width='wide', locale=self.locale.replace('-', '_'))
        for k in wkdlist:
            fb.checkbox(value='^.show', default_value=True, label=weekdays[k], datapath='.%i' % k,
                        _set_display='.dayrow_wd%i:#?"block":"none"' % k)
        bottom.div(float='left').dock(id='tt_footer', background='transparent')

    def timetable_dh(self, parent, nodeId=None, datapath=None, tstart=None,
                     tstop=None, period=None, wkdlist=None, series=None, fired=None, **kwargs):
        """Builds a timetable, that shows appointments/events in a given range,
        eventually from multiple series (e.g. multiple calendars or operators)
        
        :param parent: a parent :ref:`contentpane`
        :param nodeId: MANDATORY. the :ref:`nodeid`
        :param datapath: MANDATORY. Allow to create a hierarchy of your data’s addresses into the datastore.
                         For more information, check the :ref:`datapath` and the :ref:`datastore` pages
        :param tstart: start time
        :param tstop: stop time
        :param period: a date period (see :meth:`decodeDatePeriod() <gnr.core.gnrdate.decodeDatePeriod>`)
        :param wkdlist: weekdays, a list of integers (0..6)
        :param series: series (a list of strings)
        :param kwargs: additional parameters will go in self.tt_pars in your callbacks
        
        See the :class:`TimeTableHook` class for callbacks that you can define"""
        assert nodeId, 'nodeId is mandatory'
        assert datapath, 'datapath is mandatory'
        assert hasattr(self, 'tt_%s_dataProvider' % nodeId), 'you must define your own loop'
        parent.styleSheet(self.tt_localcss(), cssTitle='timetablecss')
        bc = parent.borderContainer(nodeId=nodeId, datapath=datapath, _class='pbl_roundedGroup', border='1px solid gray'
                                    ,
                                    regions='^.controller.layoutregions')
        self.cssh_main(bc, storepath='.controller.conf')

        bc.data('.controller.layoutregions.left', '215px', show=False)
        top = bc.contentPane(region='top', background='gray', _class='pbl_roundedGroupLabel')
        self.tt_bottom(bc.contentPane(region='bottom', datapath='.controller', _class='pbl_roundedGroupBottom'),
                       wkdlist)
        self.tt_left(bc.borderContainer(region='left', datapath='.controller', border_right='1px solid gray'), wkdlist)
        bc.contentPane(region='center').remote('ttdh_main', nodeId=nodeId, tstart=tstart, tstop=tstop, period=period,
                                               wkdlist=wkdlist, series=series, fired=fired, **kwargs)

    def tt_prepareFloating(self, pane, cbname):
        floatingPars = dict(_class='shadow_4', closable=True, dockable=True, dockTo='tt_footer', top='100px',
                            left='300px', visible=False)
        getattr(self, cbname)(pane, **floatingPars)


    def remote_ttdh_main(self, pane, tstart=None, tstop=None, period=None, wkdlist=None, fired=None, nodeId=None,
                         series=None, **kwargs):
        if not period:
            return
        self.tt_pars = dict(tstart=tstart, tstop=tstop, period=period, wkdlist=wkdlist, nodeId=nodeId, series=series,
                            minute_w=6, sh=30)
        self.tt_pars.update(kwargs)
        if hasattr(self, 'tt_%s_onstart' % nodeId):
            getattr(self, 'tt_%s_onstart' % nodeId)()

        tstart, tstop, period, wkdlist, nodeId, series, minute_w, sh = [self.tt_pars[key] for key in
                                                                        'tstart,tstop,period,wkdlist,nodeId,series,minute_w,sh'.split(
                                                                                ',')]
        days = self.tt_periodSlots()
        slot_type = self.tt_pars['slot_type']
        slot_height = getattr(self, 'tt_%s_slot_%s' % (nodeId, slot_type))()
        #cb_palette_list = sorted([func_name for func_name in dir(self) if func_name.startswith('tt_palette_')])
        #for cbname in cb_palette_list:
        #    self.tt_prepareFloating(pane,cbname)
        self.tt_pars['slot_height'] = slot_height
        day_height = slot_height * len(series) + 1
        if day_height < 50:
            day_height = 50
        ttboxwidth = '%ipx' % ((tstop.hour + 1 - tstart.hour) * 60 * self.tt_pars['minute_w'])
        ttbox = pane.div(zoomFactor='^.controller.zoom', width=ttboxwidth)
        for j, dayrow in enumerate(days):
            day = dayrow['day']
            dataserie = dayrow['dataserie']
            row = ttbox.div(_class='dayrow dayrow_wd%i' % day.weekday(),
                            height='%ipx' % day_height)
            labelcolumn = row.div(_class='labelcolumn')
            contentcolumn = row.div(_class='contentcolumn')
            self.tt_daylabel(labelcolumn, day)
            self.tt_daycontent(contentcolumn, dataserie)

    def tt_daylabel(self, cell=None, day=None):
        if hasattr(self, 'tt_%s_daylabel' % self.tt_pars['nodeId']):
            return getattr(self, 'tt_%s_daylabel' % self.tt_pars['nodeId'])(cell, day=day)
        daylabel = cell.div(_class='daylabel', **rect(top=1, bottom=1, left=1, right=1))
        daylabel.div(toText(day, format='eeee', locale=self.locale), _class='daylabel_wd daylabel_wd%i' % day.weekday())
        daylabel.div(toText(day, format='d', locale=self.locale), _class='daylabel_day')
        daylabel.div(toText(day, format='MMMM', locale=self.locale), _class='daylabel_month')

    def tt_daycontent(self, cell, dataserie, **kwargs):
        pane = cell.div(_class='daycontent', **rect(top=1, bottom=1, left=1, right=1))
        minute_w = self.tt_pars['minute_w']
        sh = self.tt_pars['slot_height']
        start_hour = self.tt_pars['tstart'].hour
        for ns, ks in enumerate(dataserie.items()):
            s_top = ns * sh
            key, slots = ks
            serierow = pane.div(_class='serierow_n%i' % ns, **rect(left=0, right=0, top=s_top, height=sh))
            for slot in slots:
                left = ((slot['ts'].hour - start_hour) * 60 + slot['ts'].minute) * minute_w
                width = slot['minutes'] * minute_w
                slotcell = serierow.div(_class='tt_slot', **rect(left=left + 1, width=width - 2))
                self.tt_slot(slotcell, slot=slot, width=width)

    def tt_periodSlots(self):
        result = []
        series = self.tt_pars['series']
        provider_handler = getattr(self, 'tt_%s_dataProvider' % self.tt_pars['nodeId'])
        for day in dayIterator(self.tt_pars['period'], locale=self.locale, workdate=self.workdate,
                               wkdlist=self.tt_pars['wkdlist']):
            dataserie = dict()
            for serie in series:
                r = provider_handler(day=day, serie=serie)
                dataserie[serie['code']] = r
            result.append(dict(dataserie=dataserie, day=day))
        return result

    def tt_slot(self, cell, **kwargs):
        getattr(self, 'tt_%s_slot_%s' % (self.tt_pars['nodeId'], self.tt_pars['slot_type']))(pane=cell, **kwargs)

    def tt_localcss(self):
        return """
        .dayrow{
            position: relative;
            border-bottom: 1px solid gray;
        }
        .labelcolumn{            
            width:70px;
            top:0;
            left:0;
            bottom:0;
            position:absolute;
        }
        .contentcolumn{
            left:70px;
            top:0;
            bottom:0;
            right:0;
            position:absolute;
        }
        .daylabel{
            border: 1px solid #7a9186;
            background-color: #ecffdc;
            z-index: 10;
            text-align: center;
            -moz-border-radius:6px;
            -webkit-border-radius:6px;
            position:absolute;
            top:1px;
            left:1px;
            right:1px;
            bottom:1px;
        }
        
        .daylabel_wd0{background-color: #ff7b83;}
        .daylabel_wd1{background-color: #bf5b63;}
        .daylabel_wd2{background-color: #8f4348;}
        .daylabel_wd3{background-color: #f0de88;}
        .daylabel_wd4{background-color: #cebe74;}
        .daylabel_wd5{background-color: #a6995d;}
        .daylabel_wd6{background-color: #a4c9a5;}
        
        .daylabel_wd{
                    -moz-border-radius-topleft:6px;
                    -moz-border-radius-topright:6px;
                    -webkit-border-top-right-radius:6px;
                    -webkit-border-top-left-radius:6px;
                    font-size: .9em;
                    font-weight: bold;
                    color: white;
        }
     
        .daylabel_day{
            font-size: 1.5em;
        }
        .daylabel_month{
            position:absolute;
            bottom:0;
            left:0;
            right:0;
            font-size: .8em;
        }
        
        .dayrow_wd0{background-color: rgba(250,250,250,0.72);display:block;}
        .dayrow_wd1{background-color: rgba(240,240,240,0.72);display:block;}
        .dayrow_wd2{background-color: rgba(230,230,230,0.72);display:block;}
        .dayrow_wd3{background-color: rgba(220,220,220,0.72);display:block;}
        .dayrow_wd4{background-color: rgba(210,210,210,0.72);display:block;}
        .dayrow_wd5{background-color: rgba(200,200,200,0.72);display:block;}
        .dayrow_wd6{background-color: rgba(190,190,190,0.72);display:block;}
        
        
        .daycontent{
        }
        
        .tt_slot{
            /*embedded position absolute; left; width;*/
            top:3px;
            bottom:3px;
            -moz-border-radius:6px;
            -webkit-border-radius:6px;
            -moz-box-shadow:1px 1px 1px #403b3b;
            -webkit-box-shadow:1px 1px 1px #403b3b;
            opacity: .8;
            background-color:white;
        }
        .ttslot_T{
            -moz-border-radius-topleft:6px;
            -moz-border-radius-topright:6px;
            -webkit-border-top-right-radius:6px;
            -webkit-border-top-left-radius:6px;
        }
        .serierow_n0{
        }
        .serierow_n1{
        }
        .serierow_n2{
        }
        .serierow_n3{}
        .serierow_n4{}
        .serierow_n5{}
        .serierow_n6{}
        .serierow_n6{}"""

class TimeTableHooks(object):
    """Hooks for TimeTable component"""

    def tt_NODEID_onstart(self):
        """Called before the timetable is drawn.
        You can use self.tt_pars to cache stuff.
        You must set self.tt_pars to a list of dictionaries (they are a list of whatever you passed in the timetable_dh,
        generally strings).
        (tt_pars won't conflict with more than one timetable, because they'd be called in multiple remote calls)
        """

    def tt_NODEID_dataProvider(self, day=None, serie=None):
        """Returns appointments/events for the specified day in the specified serie
        
        :param day: a datetime
        :param serie: a string
        
        You can also set self.tt_pars['slot_type'] to your slot type"""

    def tt_NODEID_slot_SLOTTYPE(self, pane=None, slot=None, width=None, height=None):
        """Callback to draw your slot.
        You should add your content as a child of pane
        
        :param pane: a pane where you should put your content
        :param slot: your data (from tt_NODEID_dataProvider)
        :param width: avaiable horizontal space
        :param height: avaiable vertical space
        
        If your content is larger than (width x height), the layout may look bad.
        
        It will be called once with all parameters set to None, to get the height for this slot type."""

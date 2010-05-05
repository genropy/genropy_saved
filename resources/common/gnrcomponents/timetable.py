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
from babel import dates

def rect(**kwargs):
    result = dict(position='absolute')
    for k,v in kwargs.items():
        if v is not None:
            result[k] = '%ipx' %v
    return result

class Timetable(BaseComponent):
    py_requires='foundation/tools:RemoteBuilder,foundation/tools:CSSHandler'
    css_requires='public'
    def tt_colorPaletteMenu(self,parent):
        parent.div().menu(modifiers='*',id='tt_colorPaletteMenu',_class='colorPaletteMenu',
                            connect_onOpen="""
                                            var path= this.widget.originalContextTarget.sourceNode.absDatapath();
                                             SET _temp.ttcolor=path;""",
                        ).menuItem(datapath='^_temp.ttcolor').colorPalette(value='^.color',connect_ondblclick='dijit.byId("tt_colorPaletteMenu").onCancel();')
        
        
    def timetable_dh(self,parent,nodeId=None,datapath=None,tstart=None,
                    tstop=None,period=None,wkdlist=None,series=None,fired=None):
        assert nodeId,'nodeId is mandatory'
        assert datapath,'datapath is mandatory'
        assert hasattr(self,'tt_%s_dataProvider'%nodeId), 'you must define your own loop'
        parent.styleSheet(self.tt_localcss(),cssTitle='timetablecss')
        bc = parent.borderContainer(nodeId=nodeId,datapath=datapath,_class='pbl_roundedGroup',border='1px solid gray',
                                    regions='^.controller.layoutregions')
        bc.data('.controller.layoutregions.left','215px',show=False)
        top = bc.contentPane(region='top',background='gray',_class='pbl_roundedGroupLabel')
        self.tt_bottom(bc.contentPane(region='bottom',datapath='.controller',_class='pbl_roundedGroupBottom'),wkdlist)
        self.tt_left(bc.borderContainer(region='left',datapath='.controller.conf',border_right='1px solid gray'),wkdlist)
        top.dataController("""
                            var kw = $2.kw;
                            console.log(arguments)
                            if(kw.reason){
                                var selectorText = kw.reason.attr._selectorText;
                                var convertToPx = kw.reason.attr._convertToPx;
                                var value = $1.getValue();
                                var s={}
                                s[$1.label]=convertToPx?value+'px':value;
                                console.log(s);
                                genro.dom.setSelectorStyle(selectorText,s);
                            }
                            """,
                            conf="^.controller.conf")
        center = bc.contentPane(region='center')
        self.lazyContent(center,'ttdh_main',nodeId=nodeId,tstart=tstart,tstop=tstop,period=period,
                        wkdlist=wkdlist,series=series,fired=fired)


    def tt_left(self,bc,wkdlist):
        center = bc.contentPane(region='center')
        self.tt_colorPaletteMenu(center)

        fb = center.formbuilder(cols=2, border_spacing='2px',datapath='.dayrow.day')
        weekdays = dates.get_day_names(width='wide', locale=self.locale.replace('-','_'))
        for k in wkdlist:
            fb.div(background='^.color',lbl=weekdays[k],datapath='.%i'%k,border='1px solid black',baseClass='no_background',
                    height='12px',width='12px',connectedMenu='tt_colorPaletteMenu')
        
        fb = center.formbuilder(cols=1, border_spacing='2px',width='80%')
        fb.horizontalSlider(value='^.dayrow.height',lbl='Height',minimum=30,
                            maximum=100,intermediateChanges=True,_selectorText='.dayrow',_convertToPx=True)
        
        fb.horizontalSlider(value='^.daylabel.width',lbl='Daylabel',minimum=30,
                            maximum=100,intermediateChanges=True,_selectorText='.daylabel',_convertToPx=True)
        #fb.dataController("""var dayrowstyle = genro.dom.getSelectorBag('.dayrow');
        #                        SET .dayrows.height = parsInt(dayrowstyle.getItem("height"));
        #                    """,_onStart=100)
        #fb.dataController("genro.dom.setSelectorStyle('.dayrow',{height:h+'px'});",
        #                h="^.dayrow.height",)
        
    def tt_bottom(self,bottom,wkdlist):
        bottom.horizontalSlider(value='^.zoom', minimum=.2, maximum=3,
                                intermediateChanges=True,width='15em',float='right')
        bottom.data('.zoom',1)         
        btn = bottom.button('!!Configuration',action='SET .layoutregions.left?show=!GET .layoutregions.left?show',
                            float='left')
        fb = bottom.formbuilder(cols=7, border_spacing='2px',datapath='.dayrow.day')
        weekdays = dates.get_day_names(width='wide', locale=self.locale.replace('-','_'))
        for k in wkdlist:
            fb.checkbox(value='^.show', default_value=True,label=weekdays[k],datapath='.%i' %k)
            
    def remote_ttdh_main(self,pane,tstart=None,tstop=None,period=None,wkdlist=None,fired=None,nodeId=None,series=None):
        self.tt_pars = dict(tstart=tstart,tstop=tstop,period=period,wkdlist=wkdlist,nodeId=nodeId,series=series)
        if hasattr(self,'tt_%s_onstart' %nodeId):
            getattr(self,'tt_%s_onstart' %nodeId)()
        days = self.tt_periodSlots()
        ttbox = pane.div(zoomFactor='^.controller.zoom')
        for j,dayrow in enumerate(days):
            day = dayrow['day']
            dataserie = dayrow['dataserie']
            row = ttbox.div(_class='dayrow dayrow_w%i' %day.weekday())
            self.tt_daylabel(row.div(**rect(top=0,bottom=0,left=0)),day)
            #self.tt_daycontent(row.div(left='^.controller.conf.weekday.width',**rect(top=0,bottom=0,right=0)),dataserie)
            
    def tt_daylabel(self,cell=None,day=None):
        if hasattr(self,'tt_%s_daylabel' %self.tt_pars['nodeId']):
            return getattr(self,'tt_%s_daylabel' %self.tt_pars['nodeId'])(cell,day=day)
        pane = cell.div(_class='daylabel',**rect(top=1,bottom=1,left=1,right=1))
        pane.div(toText(day,format='eeee',locale=self.locale),_class='daylabel_wd daylabel_wd%i' %day.weekday())
        pane.div(toText(day,format='d',locale=self.locale),_class='daylabel_day')
        pane.div(toText(day,format='MMMM',locale=self.locale),_class='daylabel_month')
    
    def tt_daycontent(self,cell,dataserie,**kwargs):
        pane = cell.div(_class='dayContent',**rect(top=1,bottom=1,left=1,right=1))
        #sh = day_h/len(dataserie)
        minute_w = 6
        sh = 30
        start_hour = self.tt_pars['tstart'].hour
        for ns,ks in enumerate(dataserie.items()):
            s_top=ns*sh 
            key,slots=ks
            serierow = pane.div(**rect(left=0,top=s_top,height=sh))
            for slot in slots:
                left = ((slot['ts'].hour-start_hour)*60+slot['ts'].minute)*minute_w
                width = slot['minutes'] *minute_w
                slotcell = serierow.div(**rect(top=1,left=left+1,bottom=1,width=width-1))
                #_class='ttslot %s' %status,
                self.tt_slot(slotcell,slot=slot,width=width,height=sh)
            
    def tt_periodSlots(self):
        #wkdlist = [int(k) for k,v in wkdlist.items() if v] or None
        result = []
        series = self.tt_pars['series']
        provider_handler = getattr(self,'tt_%s_dataProvider' %self.tt_pars['nodeId'])
        for day in dayIterator(self.tt_pars['period'],locale=self.locale,workdate=self.workdate,wkdlist=self.tt_pars['wkdlist']):
            dataserie = dict()
            for serie in series:
                print serie
                r =  provider_handler(day=day,serie=serie)
                print r
                dataserie[serie['code']] = r
            result.append(dict(dataserie=dataserie,day=day))
        return result
                
    def tt_slot(self,cell=None,**kwargs):
        getattr(self,'tt_%s_slot' %self.tt_pars['nodeId'])(cell,**kwargs)
        
    def tt_localcss(self):
        return """
        .dayrow{
            height: 50px;
            position: relative;
            border-bottom: 1px solid gray;
        }
        .daylabel{
            border: 1px solid #7a9186;
            background-color: #ecffdc;
            width:70px;
            z-index: 10;
            text-align: center;
            -moz-border-radius:6px;
            -webkit-border-radius:6px;
        }
        
        .daylabel_wd0{background-color: #ff7b83;}
        .daylabel_wd1{background-color: #bf5b63;}
        .daylabel_wd2{background-color: #8f4348;}
        .daylabel_wd3{background-color: #f0de88;}
        .daylabel_wd4{background-color: #cebe74;}
        .daylabel_wd5{background-color: #a6995d;}
        .daylabel_wd6{background-color: #a4c9a5;}
        .daylabel_wd{-moz-border-radius-topleft:6px;
                    -moz-border-radius-topright:6px;
                    -webkit-border-top-right-radius:6px;
                    -webkit-border-top-left-radius:6px;
                    font-size: .9em;
                    font-weight: bold;
                    color: white;}
     
        .daylabel_day{
            font-size: 1.5em;
        }
        .daylabel_month{
            font-size: .8em;
        }
        
        .dayrow_wd0{background-color: rgba(250,250,250,0.72);}
        .dayrow_wd1{background-color: rgba(240,240,240,0.72);}
        .dayrow_wd2{background-color: rgba(230,230,230,0.72);}
        .dayrow_wd3{background-color: rgba(220,220,220,0.72);}
        .dayrow_wd4{background-color: rgba(210,210,210,0.72);}
        .dayrow_wd5{background-color: rgba(200,200,200,0.72);}
        .dayrow_wd6{background-color: rgba(190,190,190,0.72);}
        """
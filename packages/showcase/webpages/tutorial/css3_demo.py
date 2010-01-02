#!/usr/bin/env pythonw
# -*- coding: UTF-8 -*-

from gnr.web.gnrwebpage import GnrWebPage

class GnrCustomWebPage(object):
    py_requires='public:Public'
        
    def main(self, rootBC, **kwargs):
        bc,top,bottom = self.pbl_rootBorderContainer(rootBC,'!!Test CSS3')
        top=bc.contentPane(region='left',width='500px',splitter=True)
        fb=top.formbuilder(col=1,datapath='controls')
        self.sizingMaker(fb,lbl='Shape rect',datapath='.shape')
        self.marginMaker(fb,lbl='Margins',datapath='.margin')

        self.colorMaker(fb,lbl='Background Color',datapath='.background')
        self.colorMaker(fb,lbl='Shadow Color',datapath='.shadow')
        self.shadowPosition(fb,lbl='Shadow position',datapath='.shadow')
        self.borderMaker(fb,lbl='Border',datapath='.border')
        self.colorMaker(fb,lbl='Border Color',datapath='.border')
        self.gradientMaker(fb,lbl='Gradient',datapath='.gradient')
        self.colorMaker(fb,lbl='Gradient from Color',datapath='.gradient_from')
        self.colorMaker(fb,lbl='Gradient to Color',datapath='.gradient_to')
        self.colorMaker(fb,lbl='Gradient color stop',datapath='.gradient_stop')
        center=bc.contentPane(region='center')
        d=center.div(width='^controls.shape.width_px', height='^controls.shape.height_px',style='^rectstyle')
        center.dataFormula('rectstyle',"dataTemplate(_template,_data)",
                  _template="""-webkit-box-shadow: $shadow.hor_px $shadow.ver_px $shadow.blur_px $shadow.color; 
                                -moz-box-shadow: $shadow.hor_px $shadow.ver_px $shadow.blur_px $shadow.color; 
                                -webkit-border-radius: $shape.style_round;
                                -moz-border-radius: $shape.style_round;
                                background-color:$background.color;
                                border:$border.width_px $border.style $border.color;
                                margin-top:$margin.top_px;
                                margin-left:$margin.left_px;
                                background-image: -webkit-gradient($gradient.type, $gradient.position_start, $gradient.position_end,
                                from($gradient_from.color), to($gradient_to.color),color-stop($gradient.colorstop, $gradient_stop.color));
                                """,
                  _data='^controls')
                
    def sizingMaker(self,pane,lbl,datapath):
        fb= pane.formbuilder(cols=3,datapath=datapath,lbl=lbl,lblpos='T')
        fb.horizontalslider(lbl='!!Base', value = '^.base', width='100px', minimum=0, maximum=100,
                                          default_value=30,intermediateChanges=True)
        fb.horizontalslider(lbl='!!Height', value = '^.height', width='100px', minimum=0, maximum=100,
                                          default_value=20,intermediateChanges=True)
        fb.dataFormula('.height_px', "Math.ceil(height)*4+'px'", height='^.height')
        fb.dataFormula('.width_px', "Math.ceil(base)*4+'px'", base='^.base')
        fb.horizontalslider(lbl='!!Round Corners', value = '^.round', width='100px', minimum=0, maximum=100,intermediateChanges=True)
        fb.dataFormula('.style_round', "Math.ceil(round)+'px'", round='^.round')
        
    def gradientMaker(self,pane,lbl,datapath):
        fb= pane.formbuilder(cols=4,datapath=datapath,lbl=lbl,lblpos='T')
        positions='top:top,left top :left top,left:left,left bottom:left bottom,botton:bottom,right bottom:right bottom,right:right,right top:right top'
        fb.filteringSelect(lbl='!!Type',width='5em', value = '^.type',values='linear:linear,radial:radial')

        fb.filteringSelect(lbl='!!Start', width='7em', value = '^.position_start',values=positions)
        fb.filteringSelect(lbl='!!End', width='7em', value = '^.position_end',values=positions)
        fb.horizontalslider(lbl='!!Colorstop', value = '^.colorstop', width='100px', minimum=0, maximum=1,intermediateChanges=True)

     
        
    def borderMaker(self,pane,lbl,datapath):
        fb= pane.formbuilder(cols=3,datapath=datapath,lbl=lbl,lblpos='T')
        fb.horizontalslider(lbl='!!Width', value = '^.width', width='100px', minimum=0, maximum=30,intermediateChanges=True)
        fb.dataFormula('.width_px',"Math.ceil(width)+'px'",width='^.width')
        fb.filteringSelect(lbl='!!Style', value = '^.style',values='solid:solid,dotted:dotted,dashed:dashed,double:double')
        
    def marginMaker(self,pane,lbl,datapath):
        fb= pane.formbuilder(cols=2,datapath=datapath,lbl=lbl,lblpos='T')
        fb.horizontalslider(lbl='!!Top', value = '^.top', width='100px', minimum=0, maximum=200,
                                         default_value=20,intermediateChanges=True)
        fb.dataFormula('.top_px',"Math.ceil(top)+'px'",top='^.top')
        fb.horizontalslider(lbl='!!Left', value = '^.left', width='100px', minimum=0, maximum=200,
                                         default_value=20,intermediateChanges=True)
        fb.dataFormula('.left_px',"Math.ceil(left)+'px'",left='^.left')
        
    def shadowPosition(self,pane,lbl,datapath):
        fb= pane.formbuilder(cols=3,datapath=datapath,lbl=lbl,lblpos='T')
        fb.horizontalslider(lbl='!!Horizontal', value = '^.hor', width='100px', minimum=-50, maximum=50, 
                            discreteValues='100', default_value=0,intermediateChanges=True)
        fb.dataFormula('.hor_px',"Math.ceil(hor)+'px'",hor='^.hor')
        fb.horizontalslider(lbl='!!Vertical', value = '^.ver', width='100px', minimum=-50, maximum=50, 
                            discreteValues='100', default_value=0,intermediateChanges=True)
        fb.dataFormula('.ver_px',"Math.ceil(ver)+'px'",ver='^.ver')
        fb.horizontalslider(lbl='!!Blur', value = '^.blur', width='100px', minimum=0, maximum=50, 
                            discreteValues='50', default_value=0,intermediateChanges=True)
        fb.dataFormula('.blur_px',"Math.ceil(blur)+'px'",blur='^.blur')
                                  
    def colorMaker(self,pane,lbl,datapath):
        fb= pane.formbuilder(cols=3,datapath=datapath,lbl=lbl,lblpos='T')
        fb.horizontalslider(lbl='!!Red', value = '^.red', width='100px', minimum=0, maximum=255, 
                            discreteValues='256', default_value=128,intermediateChanges=True)
        fb.horizontalslider(lbl='!!Green', value = '^.green', width='100px', minimum=0, maximum=255, 
                            discreteValues='256', default_value=128,intermediateChanges=True)
        fb.horizontalslider(lbl='!!Blue', value = '^.blue', width='100px', minimum=0, maximum=255,
                            discreteValues='256', default_value=128,intermediateChanges=True)
        fb.dataFormula('.color', "'#'+red.toString(16)+green.toString(16)+blue.toString(16)", 
                                red='^.red', green='^.green', blue='^.blue',_init=True)
        
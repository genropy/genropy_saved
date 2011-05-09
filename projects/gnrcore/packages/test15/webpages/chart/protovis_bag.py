# -*- coding: UTF-8 -*-

# palette_manager.py
# Created by Francesco Porcari on 2010-12-27.
# Copyright (c) 2010 Softwell. All rights reserved.
 
"""Test Protovis"""

   
from gnr.core.gnrbag import Bag
import random


class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerFull"
    js_requires='protovis'
    
    def test_1_SimpleBar(self, pane):
        """Simlple Bar"""
       
        pane = pane.div()
        pane.data('.intermediate', False)
        pane.data('.timing', 0)
        pane.data('.pvstore.source', self.source_SimpleBar())
        pane.data('.pvstore.width', 300)
        pane.data('.pvstore.height', 200)
        pane.data('.pvstore.ys', 80)
        pane.data('.pvstore.xs', 20)
        pane.dataRpc('.pvstore.data', 'random_data', _fired="^.update_data",_init=True,_timing='^.timing')
        fb= pane.formbuilder(cols=2, border_spacing='0px')
        fb_pars= fb.div().formbuilder(cols=1, border_spacing='2px')
        fb_draw= fb.div().formbuilder(cols=1, border_spacing='2px')
        fb_draw.div().span('Update data every: ')._.span('^.timing')._.span(' seconds')
        fb_draw.div(border='1px solid silver',margin='5px',background_color='white').protovis(nodeId='pv_1',storepath='.pvstore')
        fb_pars.horizontalslider(value="^.pvstore.width", minimum=200, maximum=500, intermediateChanges='^.intermediate',
                            width='150px', lbl='Width')
        fb_pars.horizontalslider(value="^.pvstore.height", minimum=100, maximum=300, intermediateChanges='^.intermediate',
                            width='150px', lbl='Height')
        fb_pars.horizontalslider(value="^.pvstore.ys", minimum=10, maximum=100, intermediateChanges='^.intermediate',
                            width='150px', lbl='Y')
        fb_pars.horizontalslider(value="^.pvstore.xs", minimum=5, maximum=50, intermediateChanges='^.intermediate',
                            width='150px', lbl='X')
        
        fb_pars.horizontalslider(value="^.timing", minimum=0, maximum=10, intermediateChanges=False,
                            width='150px', lbl='Timing')
        fb_pars.checkbox(value='^.intermediate',label='Intermediate changes')
        fb_pars.button("Update", fire=".update_data")
        
    
    def source_SimpleBar(self):
        result = Bag()
        visbag = result.child('Panel', 
                            width='=.width', 
                            height='=.height')
        visbag.child('Rule', 
                     data_js='pv.range(0, 2, .5)',
                     def_ys='=.ys',
                     bottom_fn_d='d * this.ys() + .5').child('Label')
                     
        visbag.child('Bar', data='=.data',
                     
                     def_ys='=.ys',
                     def_xs='=.xs',
                     width='=.xs',
                     height_fn_d='d * this.ys()',
                     bottom=0,
                     left_fn='this.index * (this.xs() +5) +10',
                     anchor='bottom').child(tag='Label')
        return result
    def test_2_MouseOver(self, pane):
        """MouseOver"""
        pane = pane.div()
        pane.data('.pvstore.source', self.source_MouseOver())
        pane.data('.pvstore.width', 300)
        pane.data('.pvstore.height', 200)
        pane.dataRpc('.pvstore.data', 'random_data', _fired="^.update_data",_init=True)
        fb= pane.formbuilder(cols=2, border_spacing='0px')
        fb_pars= fb.div().formbuilder(cols=1, border_spacing='2px')
        fb.div(border='1px solid silver',margin='5px',background_color='white').protovis(nodeId='pv_2',storepath='.pvstore')

        fb_pars.horizontalslider(value="^.pvstore.width", minimum=200, maximum=500, intermediateChanges='^.intermediate',
                            width='150px', lbl='Width')
        fb_pars.horizontalslider(value="^.pvstore.height", minimum=100, maximum=300, intermediateChanges='^.intermediate',
                            width='150px', lbl='Height')
        fb_pars.button("Update", fire=".update_data")
    
    def source_MouseOver(self):
        result = Bag()
        visbag = result.child('Panel', width='=.width', height='=.height')
        visbag.child('Bar', data='=.data',def_i=-1,
                     width='20', 
                     height_fn_d='d * 80',
                     bottom=0,
                     left_fn='this.index * 25 + 25',
                     anchor='bottom',
                     fillStyle_fn='this.i() == this.index ? "red" : "green"',
                     event_mouseover_fn='this.i(this.index)',
                     event_mouseout_fn='this.i(-1)',
                     title_fn="this.index"
                     )
        return result
        
    
    def rpc_random_data(self):
        numbers = [int(random.random() * 200) / 100. for i in range(10)]
        return '%s::JS' % str(numbers)

    #def testProtovis_(self, pane,nodeId):
        
#        
#        """new pv.Panel()
#    .width(150)
#    .height(150)
#  .add(pv.Bar)
#    .def("i", -1)
#    .data([1, 1.2, 1.7, 1.5, .7, .2])
#    .bottom(0)
#    .width(20)
#    .height(function(d) d * 80)
#    .left(function() this.index * 25)
#    .fillStyle(function() this.i() == this.index ? "red" : "black")
#    .event("mouseover", function() this.i(this.index))
#    .event("mouseout", function() this.i(-1))
#    .title(function() this.index)
#  .root.render();"""
#            
#  """
# 
# 
    def _test_3_Area(self, pane):
        """Area"""
       
        pane = pane.div()
        pane.data('.intermediate', False)
        pane.data('.timing', 0)
        pane.data('.pvstore.source', self.source_Area())
        pane.data('.pvstore.width', 300)
        pane.data('.pvstore.height', 200)
        pane.data('.pvstore.ys', 80)
        pane.data('.pvstore.xs', 20)
        pane.dataRpc('.pvstore.data', 'random_data', _fired="^.update_data",_init=True,_timing='^.timing')
        fb= pane.formbuilder(cols=2, border_spacing='0px')
        fb_pars= fb.div().formbuilder(cols=1, border_spacing='2px')
        fb_draw= fb.div().formbuilder(cols=1, border_spacing='2px')
        fb_draw.div().span('Update data every: ')._.span('^.timing')._.span(' seconds')
        fb_draw.div(border='1px solid silver',margin='5px',background_color='white').protovis(nodeId='pv_3',storepath='.pvstore')
      #fb_pars.horizontalslider(value="^.pvstore.width", minimum=200, maximum=500, intermediateChanges='^.intermediate',
      #                    width='150px', lbl='Width')
      #fb_pars.horizontalslider(value="^.pvstore.height", minimum=100, maximum=300, intermediateChanges='^.intermediate',
      #                    width='150px', lbl='Height')
      #fb_pars.horizontalslider(value="^.pvstore.ys", minimum=10, maximum=100, intermediateChanges='^.intermediate',
      #                    width='150px', lbl='Y')
      #fb_pars.horizontalslider(value="^.pvstore.xs", minimum=5, maximum=50, intermediateChanges='^.intermediate',
      #                    width='150px', lbl='X')
      #
      #fb_pars.horizontalslider(value="^.timing", minimum=0, maximum=10, intermediateChanges=False,
      #                    width='150px', lbl='Timing')
      #fb_pars.checkbox(value='^.intermediate',label='Intermediate changes')
        fb_pars.button("Update", fire=".update_data")
        
    
    def source_Area(self):
        result = Bag()
        
        result.child('env','w',400)
        result.child('env','h',200)
        result.child('env','data',"""pv.range(0, 10, .1).map(function(x) {
                                            return {x: x, y: Math.sin(x) + Math.random() * .5 + 2};
                                          })""")
        result.child('env','sx',"pv.Scale.linear(data, function(d) d.x).range(0, w)")
        result.child('env','sy',"pv.Scale.linear(0, 4).range(0, h)")

        visbag = result.child('Panel', 
                            width_js='w', 
                            height_js='h',
                            bottom=20,
                            left=20,
                            right=10,
                            top=5)
        visbag.child('Rule', 
                     data_js='sy.ticks(5)',
                     bottom_js='sy',
                     strokeStyle_fn_d='d ?  "#eee" : "#000"',
                     anchor='left'
                     ).child('Label',text_js='sy.tickFormat')
                     
        visbag.child('Rule', 
                     data_js='sx.ticks()',
                     visible_fn_d='d',
                     left_js='sx',
                     bottom=-5,
                     height=5,
                     anchor='bottom'
                     ).child('Label',text_js='sx.tickFormat')

        visbag.child('Area', data_js='data',
                     bottom=1,
                     left_fn_d='sx(d.x)',
                     height_fn_d='sy(d.y)',
                     fillStyle="rgb(121,173,210)",
                     anchor="top").child(tag='Line',lineWidth='3')
        return result
#/* Sizing and scales. */
#var w = 400,
#    h = 200,
#    x = pv.Scale.linear(data, function(d) d.x).range(0, w),
#    y = pv.Scale.linear(0, 4).range(0, h);
#
#/* The root panel. */
#var vis = new pv.Panel()
#    .width(w)
#    .height(h)
#    .bottom(20)
#    .left(20)
#    .right(10)
#    .top(5);
#
#/* Y-axis and ticks. */
#vis.add(pv.Rule)
#    .data(y.ticks(5))
#    .bottom(y)
#    .strokeStyle(function(d) d ? "#eee" : "#000")
#  .anchor("left").add(pv.Label)
#    .text(y.tickFormat);
#
#/* X-axis and ticks. */
#vis.add(pv.Rule)
#    .data(x.ticks())
#    .visible(function(d) d)
#    .left(x)
#    .bottom(-5)
#    .height(5)
#  .anchor("bottom").add(pv.Label)
#    .text(x.tickFormat);
#
#/* The area with top line. */
#vis.add(pv.Area)
#    .data(data)
#    .bottom(1)
#    .left(function(d) x(d.x))
#    .height(function(d) y(d.y))
#    .fillStyle("rgb(121,173,210)")
#  .anchor("top").add(pv.Line)
#    .lineWidth(3);
#
#vis.render();
#            
#            """
#
#             
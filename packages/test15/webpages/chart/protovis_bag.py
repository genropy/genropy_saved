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
        fb_draw.div().span('Updatedtata every')._.span('^.timing')
        fb_draw.div(border='1px solid silver',margin='5px').protovis(nodeId='pv_1',storepath='.pvstore')
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
        fb.div(border='1px solid silver',margin='5px').protovis(nodeId='pv_1',storepath='.pvstore')

        fb_pars.horizontalslider(value="^.pvstore.width", minimum=200, maximum=500, intermediateChanges='^.intermediate',
                            width='150px', lbl='Width')
        fb_pars.horizontalslider(value="^.pvstore.height", minimum=100, maximum=300, intermediateChanges='^.intermediate',
                            width='150px', lbl='Height')
        fb_pars.button("Update", fire=".update_data")
    
    def source_MouseOver(self):
        result = Bag()
        visbag = result.child('Panel', width='=.width', height='=.height')
       # visbag.child('Rule', data='pv.range(0, 2, .5)::JS',
       #              bottom='function(d){return d * 80 + .5}::JS').child('Label')
        visbag.child('Bar', data='=.data',def_i=-1,
                     width='20', 
                     height_fn_d='d * 80',
                     bottom=0,
                     left_fn='this.index * 25 + 25',
                     anchor='bottom',
                     fillStyle_fn='this.i() == this.index ? "red" : "green"',
                     event_mouseover_fn='this.i(this.index)',
                     event_mouseout_fn='this.i(-1)' 
                     ).child(tag='Label')
        return result
        
    def rpc_random_data(self):
        numbers = [int(random.random() * 200) / 100. for i in range(10)]
        return '%s::JS' % str(numbers)

    #def testProtovis_(self, pane,nodeId):
        
        
        """new pv.Panel()
    .width(150)
    .height(150)
  .add(pv.Bar)
    .def("i", -1)
    .data([1, 1.2, 1.7, 1.5, .7, .2])
    .bottom(0)
    .width(20)
    .height(function(d) d * 80)
    .left(function() this.index * 25)
    .fillStyle(function() this.i() == this.index ? "red" : "black")
    .event("mouseover", function() this.i(this.index))
    .event("mouseout", function() this.i(-1))
    .title(function() this.index)
  .root.render();"""
            

             
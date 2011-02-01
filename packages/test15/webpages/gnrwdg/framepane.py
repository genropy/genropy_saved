# -*- coding: UTF-8 -*-

# slotbar.py
# Created by Francesco Porcari on 2011-01-30.
# Copyright (c) 2011 Softwell. All rights reserved.

from gnr.web.gnrwebstruct import struct_method
"Test page description"
class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerFull"

    def windowTitle(self):
        return 'SlotBar test'
         
    def test_0_slotbar_base(self,pane):
        """Design headline"""
        pane.makeDemoFrame()
    
    def test_1_slotbar_sidebar(self,pane):
        """Design sidebar"""
        pane.makeDemoFrame(design='sidebar')
    
    def test_2_slotbar_sidebar(self,pane):
        """Change gradients"""
        pane.makeDemoFrame(design='sidebar',gradient_from='blue',gradient_to='navy')
        
    
    @struct_method
    def makeDemoFrame(self,pane,design=None,gradient_from=None,gradient_to=None):
        frame = pane.framePane(frameCode='frameOne',height='200px',width='300px',shadow='3px 3px 5px gray',
                                border='1px solid #bbb',margin='10px',center_border='1px solid #bbb',
                                center_background='gray',
                                side_gradient_from=gradient_from,
                                side_gradient_to=gradient_to,
                                rounded=10,design=design)
        top = frame.top.slotToolbar(slots='30,foo,*,bar,30',height='20px')
        bottom = frame.bottom.slotToolbar(slots='30,foo,*,bar,30',height='20px')
        left = frame.left.slotToolbar(slots='30,foo,*,bar,30',width='20px')
        right = frame.right.slotToolbar(slots='30,foo,*,bar,30',width='20px')
        top.foo.button(label='Add',iconClass='icnBaseAdd',showLabel=False)
        top.bar.button(label='Del',iconClass='icnBaseOk',showLabel=False)
        bottom.foo.button(label='Add',iconClass='icnBaseAdd',showLabel=False)
        bottom.bar.button(label='Del',iconClass='icnBaseOk',showLabel=False)
        left.foo.button(label='Add',iconClass='icnBaseAdd',showLabel=False)
        left.bar.button(label='Del',iconClass='icnBaseOk',showLabel=False)
        right.foo.button(label='Add',iconClass='icnBaseAdd',showLabel=False)
        right.bar.button(label='Del',iconClass='icnBaseOk',showLabel=False)
        
        

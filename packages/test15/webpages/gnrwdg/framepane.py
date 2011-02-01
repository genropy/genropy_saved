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
        """First test description"""
        frame = pane.framePane(frameCode='frameOne',height='200px',width='200px',shadow='3px 3px 5px gray',
                                border='1px solid #bbb',rounded=10,margin='10px')
        top = frame.top.slotToolbar(slots='30,foo,*,bar,30',height='20px',rounded_top=10)
        bottom = frame.bottom.slotToolbar(slots='30,foo,*,bar,30',height='20px',rounded_bottom=10)
        left = frame.left.slotToolbar(slots='30,foo,*,bar,30',height='20px',orientation='V')
        right = frame.right.slotToolbar(slots='30,foo,*,bar,30',height='20px',orientation='V')
        top.foo.button(label='Add',iconClass='icnBaseAdd',showLabel=False)
        top.bar.button(label='Del',iconClass='icnBaseOk',showLabel=False)
        bottom.foo.button(label='Add',iconClass='icnBaseAdd',showLabel=False)
        bottom.bar.button(label='Del',iconClass='icnBaseOk',showLabel=False)
        left.foo.button(label='Add',iconClass='icnBaseAdd',showLabel=False)
        left.bar.button(label='Del',iconClass='icnBaseOk',showLabel=False)
        right.foo.button(label='Add',iconClass='icnBaseAdd',showLabel=False)
        right.bar.button(label='Del',iconClass='icnBaseOk',showLabel=False)
        frame.div(height='100%',width='100%',background_color='red')
        

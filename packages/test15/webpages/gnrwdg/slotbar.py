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
        frame = pane.framePane(frameCode='frameOne',height='100px',shadow='3px 3px 5px gray',
                                border='1px solid #bbb',rounded_top=10,margin='10px')
        top = frame.top.slotBar(slots='30,foo,|,*,|,bar',height='20px')
        top.foo.div('foo',width='100px',background='navy',lbl='Foo')
        top.bar.myslot()
        
    def test_1_slotbar(self,pane):
        """First test description"""
        frame = pane.framePane(frameCode='frameOne',height='100px',shadow='3px 3px 5px gray',
                                border='1px solid #bbb',rounded_top=10,margin='10px')
        top = frame.top.slotBar(slots='*,|,foo,bar,|,*',side='top',
                            gradient_deg=90,gradient_from='#fff',gradient_to='#bbb',
                            border_bottom='1px solid #bbb',rounded_top=10,lbl_position='T',lbl_color='red',
                            lbl_font_size='7px')
        top.foo.div('foo',width='100px',background='navy',lbl='Foo')
        top.bar.myslot()
        
    #def test_1_slotbox(self,pane):
        
    def test_2_slotToolbar(self,pane):
        """First test description"""
        frame = pane.framePane(frameCode='frameTwo',height='100px',shadow='3px 3px 5px gray',
                                border='1px solid #bbb',rounded_top=10,margin='10px')
        top = frame.top.slotToolbar(slots='*,|,foo,bar,|,*,xx',
                               gradient_deg='90',gradient_from='#fff',gradient_to='#bbb',
                               border_bottom='1px solid #bbb',rounded_top=10,lbl_position='T',lbl_color='red',
                               lbl_font_size='7px')
        top.foo.div('foo',width='100px',background='navy',lbl='labelFoo')
        top.bar.myslot()
        top.xx.div(width='1px')
        
    def test_3_slotToolbar_vertical(self,pane):
        frame = pane.framePane(frameCode='frameTwo',height='300px',shadow='3px 3px 5px gray',
                                border='1px solid #bbb',rounded_left=10,margin='10px')
        sl = frame.left.slotBar(orientation='V',slots='10,foo,*,|,bar,|,*,spam,*',
                                border_right='1px solid gray',gradient_from='#bbb',
                                gradient_to='#fff',rounded_left=10,toolbar=True)
        sl.foo.button(label='Add',iconClass='icnBaseAdd',showLabel=False)
        sl.bar.button(label='Del',iconClass='icnBaseOk',showLabel=False)
        sl.spam.div(height='18px',width='16px',background='blue')

                                
        
    @struct_method
    def myslot(self,pane):
        pane.button(label='Bar',iconClass='icnBaseAdd',lbl='Bar',showLabel=False)
    
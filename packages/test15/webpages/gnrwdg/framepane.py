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
         
    def _test_0_slotbar_base(self,pane):
        """Design headline"""
        frame = pane.framePane(frameCode='frame1',height='200px',width='300px',shadow='3px 3px 5px gray',
                                border='1px solid #bbb',margin='10px',center_border='1px solid #bbb',
                                center_background='gray',rounded_top_left=15,rounded_bottom_right=30)
        top = frame.top.slotToolbar(slots='30,foo,*,bar,30',height='20px')
        bottom = frame.bottom.slotBar(slots='btoh,*,|,bt2,30',height='30px')
        bottom.btoh.slotButton(label='Ok')
        bottom.bt2.slotButton(label='ciao ciao')


    
    def test_1_slotbar_sidebar(self,pane):
        """Design sidebar"""
        frame = pane.framePane(frameCode='frame2',height='200px',width='300px',shadow='3px 3px 5px gray',
                                border='1px solid #bbb',margin='10px',center_border='1px solid #bbb',
                                center_background='gray',rounded_top=10,design='sidebar')
        top = frame.top.slotToolbar(slots='30,foo,*,bar,30',height='20px') 
        left = frame.left.slotToolbar(slots='30,foo,*,bar,30',width='40px')
           
    def test_2_slotbar_sidebar(self,pane):
        """Change gradients"""
        frame = pane.framePane(frameCode='frame3',height='200px',width='300px',shadow='3px 3px 5px gray',
                                border='1px solid #bbb',margin='10px',center_border='1px solid #bbb',
                                center_background='gray',rounded_top=10,
                                side_gradient_from='darkblue',
                                side_gradient_to='blue')
        top = frame.top.slotToolbar(slots='30,foo,*,bar,30',height='20px') 
        left = frame.left.slotToolbar(slots='30,foo,*,bar,30',width='20px',gradient_to='red')  
        bottom = frame.bottom.slotToolbar(slots='30,foo,*,bar,30',height='20px',gradient_from='darkgreen')
        right = frame.right.slotToolbar(slots='30,foo,*,bar,30',width='20px')
        
    def test_3_slotbar_commands(self,pane):
        """Change gradients"""
        frame = pane.framePane(frameCode='frame4',height='200px',width='300px',shadow='3px 3px 5px gray',
                                border='1px solid #bbb',margin='10px',center_border='1px solid #bbb',
                                center_background='gray',rounded_top=10)
        top = frame.top.slotToolbar(slotbarCode='myslotbar',slots='*,foo,bar,10',height='20px') 
        top.foo.slotButton(label='Add',iconClass='icnBaseAdd',publish='add')
        top.bar.slotButton(label='remove',iconClass='icnBaseDelete',publish='remove')

        frame.numberTextbox(value='^.value',default_value=1,width='5em',
                            subscribe_myslotbar_add="""SET .value=(GET .value)+1;""",
                            subscribe_myslotbar_remove='SET .value= (GET .value) -1;')
     
        
        

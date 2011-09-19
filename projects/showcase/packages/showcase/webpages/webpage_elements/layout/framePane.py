# -*- coding: UTF-8 -*-

# framePane.py
# Created by Filippo Astolfi on 2011-01-30.
# Copyright (c) 2011 Softwell. All rights reserved.

"""framePane"""

class GnrCustomWebPage(object):
    py_requires = 'gnrcomponents/testhandler:TestHandlerFull'
    
    def windowTitle(self):
        return 'SlotBar test'
        
    def test_1_frame(self,pane):
        """frame"""
        frame = pane.framePane(frameCode='frame1',height='200px',
                               shadow='3px 3px 5px gray',border='1px solid #bbb',margin='10px',
                               rounded=20,design='sidebar')
        top = frame.top.slotToolbar(slots='*,test_xx,*,jeff,*,searchOn',background='pink')#,width='20px')
        top.test_xx.div('just a test',width='100px',background='red')
        top.jeff.button('I am a button', action="alert('hi')")
        frame.div('Here goes the \"center\" content.',margin='20px')
        
    def test_2_frame2(self,pane):
        """Design: headline"""
        frame = pane.framePane(frameCode='frame0',height='200px',width='300px',shadow='3px 3px 5px gray',
                               border='1px solid #bbb',margin='10px',center_border='10px solid #bbb',
                               center_background='green')
        top = frame.top.slotToolbar(slots='30,foo,*,bar,30',height='20px')
        bottom = frame.bottom.slotBar(slots='btoh,*,|,bt2,30',height='30px')
        bottom.btoh.slotButton(label='Ok',action='alert("Hello!")')
        bottom.bt2.slotButton(label='ciao ciao',action='alert("Hello again!")')
        
    def test_3_slotbar_base(self,pane):
        """Design: headline"""
        frame = pane.framePane(frameCode='frame0',height='200px',width='300px',shadow='3px 3px 5px gray',
                               border='1px solid #bbb',margin='10px',center_border='1px solid #bbb',
                               center_background='gray',design='headline')
        top = frame.top.slotToolbar(slots='30,foo,*,bar,30',height='20px')
        right = frame.right.slotToolbar(slots='30,foo,*,bar,30',width='20px')
        bottom = frame.bottom.slotBar(slots='btoh,*,|,bt2,30',height='30px')
        bottom.btoh.slotButton(label='Ok',action='alert("Hello!")')
        bottom.bt2.slotButton(label='ciao ciao',action='alert("Hello again!")')
        
    def test_4_slotbar_sidebar(self,pane):
        """Design: sidebar"""
        frame = pane.framePane(frameCode='frame1',height='200px',width='300px',shadow='3px 3px 5px gray',
                               border='1px solid #bbb',margin='10px',
                               center_background='gray',rounded=20,design='sidebar')
        right = frame.right.slotToolbar(slots='30,foo,*,bar,30',width='20px') 
        bottom = frame.bottom.slotToolbar(slots='30,foo,*,bar,30',height='20px')
        bottom.foo.button('!!Save',iconClass="icnBaseOk",showLabel=False)
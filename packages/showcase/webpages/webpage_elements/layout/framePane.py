# -*- coding: UTF-8 -*-

# framePane.py
# Created by Filippo Astolfi on 2011-01-30.
# Copyright (c) 2011 Softwell. All rights reserved.

"""Test page description"""

from gnr.web.gnrwebstruct import struct_method

class GnrCustomWebPage(object):
    py_requires = 'gnrcomponents/testhandler:TestHandlerFull'
    """
    **framePane**
    
    * *frameCode*: 
    * *rounded* (add in CSS!)
    
    New Syntax! ``frame.top.slotBar``
    
    **slotBar**
    
    * *slots* (height obbligatorio?):
        
        * "|" --> splitter bar
        * "*" --> white space
        
    * *orientation* --> V (vertical)
                    --> ? (horizontal, default)
    * *gradient_deg* 0 --> x axis, positive numbers
                    90 --> y axis, positive numbers
                   180 --> x axis, negative numbers
                   270 --> y axis, negative numbers
                   
    * *gradient_from* --> a color
    * *gradient_to* --> another color
    * *lbl_position='T'* *lbl_color='red'* *lbl_font_size='7px'* (slotBar attributes, or CSS attributes
                                                                  for every object?)
       LBL! not label (infact the slotBar is built on formbuilder... right???)
    * *border_bottom='1px solid #bbb'*
    * *showLabel=False* ???
    
    **Struct method**
        
        from gnr.web.gnrwebstruct import struct_method
        
        ...
        
        top.bar.myslot()
        
        ...
        
        @struct_method
        def myslot(self,pane):
            pane.button(label='Bar',iconClass='icnBaseAdd',lbl='Bar',showLabel=False)
    """
    
    def windowTitle(self):
        return 'SlotBar test'
        
    def test_0_slotbar_base(self,pane):
        """Test_0"""
        frame = pane.framePane(frameCode='frameOne', height='100px', shadow='3px 3px 5px gray',
                               border='1px solid #bbb', rounded_top=10, margin='10px')
        top = frame.top.slotBar(slots='30,foo,|,*,Hello,*,|,bar',height='20px')
        bottom = frame.bottom.slotBar(slots='30,foo,|,*,Hello,*,|,bar',height='20px')
        left = frame.left.slotBar(orientation='V',slots='30,foo,|,*,Hello,*,|,bar',height='20px')
        right = frame.right.slotBar(orientation='V',slots='30,foo,|,*,Hello,*,|,bar',height='20px')
        
        top.foo.div('foo',width='100px',color='white',background='navy',lbl='Foo')
        top.bar.myslot()
        
        bottom.foo.div('foo',width='100px',color='white',background='navy',lbl='Foo')
        bottom.bar.myslot()
        
    def test_1_slotbar(self,pane):
        """Test_1"""
        frame = pane.framePane(frameCode='frameTwo',height='100px',shadow='3px 3px 5px gray',
                                border='1px solid #bbb',rounded_top=10,margin='10px')
        top = frame.top.slotBar(slots='*,|,foo,bar,|,*',side='top',
                                gradient_deg=90,gradient_from='#fff',gradient_to='#bbb',
                                border_bottom='1px solid #bbb',rounded_top=10,lbl_position='T',lbl_color='red',
                                lbl_font_size='7px')
        top.foo.div('foo',width='100px',color='white',background='navy',lbl='Foo')
        top.bar.myslot()
        center = frame.center()
        fb = center.formbuilder(datapath='test3', cols=2, fld_width='100%', width='100%', lbl_color='red')
        fb.textbox(value='^.name', lbl='Name')
        fb.textbox(value='^.surname', lbl='Surname')
        fb.numberTextbox(value='^.age', lbl="Age")
        fb.textbox(value='^.mail', lbl='Mail')
        fb.filteringSelect(value='^.sex', values='M:Male,F:Female', lbl='Sex')
        fb.textbox(value='^.job.profession', lbl='Job')
        fb.textbox(value='^.job.company_name', lbl='Company name')
        fb.textbox(value='^.job.fiscal_code', lbl='Fiscal code')
        
    def test_2_slotToolbar(self,pane):
        """Test_2"""
        frame = pane.framePane(frameCode='frameThree',height='100px',shadow='3px 3px 5px gray',
                                border='1px solid #bbb',rounded_top=10,margin='10px')
        top = frame.top.slotToolbar(slots='*,|,foo,bar,|,*,xx',
                                    gradient_deg='90',gradient_from='#fff',gradient_to='#bbb',
                                    border_bottom='1px solid #bbb',rounded_top=10,lbl_position='T',lbl_color='red',
                                    lbl_font_size='7px')
        top.foo.div('foo',width='100px',color='white',background='navy',lbl='labelFoo')
        top.bar.myslot()
        top.xx.div(width='1px')
        
    def test_3_slotToolbar_vertical(self,pane):
        """Test_3"""
        frame = pane.framePane(frameCode='frameFour',height='300px',shadow='3px 3px 5px gray',
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

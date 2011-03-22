# -*- coding: UTF-8 -*-

# toolbar.py
# Created by Filippo Astolfi on 2011-03-22.
# Copyright (c) 2011 Softwell. All rights reserved.

"""slotBar and slotToolbar"""

import datetime

class GnrCustomWebPage(object):
    py_requires = 'gnrcomponents/testhandler:TestHandlerFull'
    
    def windowTitle(self):
         return 'slotBar and slotToolbar'
         
    def test_1_simple(self,pane):
        """simple example"""
        workdate = str(datetime.datetime.now().date())
        frame = pane.framePane(frameCode='dummy',height='150px',margin='10px',
                               center_background='gray',rounded=10,design='headline') # design='sidebar'
        top = frame.top.slotToolbar(slotbarCode='dummy1',slots='*,foo,*',height='20px')
        top.foo.div('Hello!')
        left = frame.left.slotToolbar(slotbarCode='dummy2',slots='*,foo,*',width='30px')
        left.foo.div('Left Hello!')
        right = frame.right.slotToolbar(slotbarCode='dummy3',slots='*,foo,*',width='30px')
        right.foo.div('Right Hello!')
        bottom = frame.bottom.slotBar(slotCode='dummy8',slots='*,foo,*',height='20px')
        bottom.foo.div('Hello! (from the bottom slotBar)')
        
    def test_2_features(self,pane):
        """Some added features"""
        workdate = str(datetime.datetime.now().date())
        frame = pane.framePane(frameCode='framecode',height='300px',shadow='3px 3px 5px gray',
                               border='1px solid #bbb',margin='10px',center_background='gray',rounded=10)
        top = frame.top.slotToolbar(slotbarCode='top',slots='10,hello,*,foo,*,dummy',height='25px')
        top.hello.div(workdate)
        top.foo.div('Schedule',font_size='14pt')
        top.dummy.button(label='add',iconClass='icnBaseAdd',showLabel=False,
                         action="alert('Added a row in your grid')")
        top.dummy.button(label='del',iconClass='icnBaseDelete',showLabel=False,
                         action="alert('Deleted a row in your grid')")
        top.dummy.button(label='email',iconClass='icnBaseEmail',showLabel=False,
                         action="alert('Sended your schedule by email')")
        top.dummy.button(label='pdf',iconClass='icnBasePdf',showLabel=False,
                         action="alert('PDF created')")
        top.dummy.button(label='print',iconClass='icnBasePrinter',showLabel=False,
                         action="alert('Printed')")
        
        left = frame.left.slotToolbar(slotbarCode='left',slots='10,new,foo,bar,dummy,*',width='40px')
        left.new.button('new grid', action="alert('New schedule!')")
        left.foo.button('save grid', action="alert('Saved!')")
        left.bar.button('load grid', action="alert('Loaded!')")
        left.dummy.button('exit', action="alert('Exited!')")
        
        bottom = frame.bottom.slotToolbar(slots='300,bar,*,searchOn',height='20px')
        bottom.bar.div('Here goes the messages for user')
        
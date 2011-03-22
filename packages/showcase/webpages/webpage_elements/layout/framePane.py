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
        frame = pane.framePane(frameCode='frame1',height='200px',shadow='3px 3px 5px gray',
                               border='1px solid #bbb',margin='10px',
                               center_background='gray',rounded=20,design='sidebar')
        top = frame.top.slotToolbar(slots='*,test_xx,*,jeff,*,searchOn')#,width='20px')
        top.test_xx.div('just a test',width='100px',background='red')
        top.jeff.button('I am a button', action="alert('hi')")
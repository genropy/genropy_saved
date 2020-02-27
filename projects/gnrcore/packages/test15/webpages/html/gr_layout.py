#!/usr/bin/python
# -*- coding: utf-8 -*-

"genro.dom.centerOn"

class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerBase"
    
    
    def test_0_formbuilder_advanced(self, pane):
        fb = pane.formbuilder(cols=3,lblpos='T',lbl_text_align='center')
        fb.div('A1',lbl='A')
        fb.div('B1',lbl='B')
        fb.div('C1',lbl='C')
       #fb.div('A2')
       #fb.div('B2')
       #fb.div('C2')
        fb.div('B3',pos='2,1')
        #fb.div('C4',pos='2,2')

    def test_1_simplegrid(self, pane):
        layout = pane.div(display='grid',height='500px',width='400px',
                        margin='10px',
                        style='grid-template-rows:50px,auto,auto,50px;'
                        #border='1px solid silver',
                        )
        
        layout.div(border='1px solid silver')
        layout.div(border='1px solid silver')
        layout.div(border='1px solid silver')
        layout.div(border='1px solid silver')
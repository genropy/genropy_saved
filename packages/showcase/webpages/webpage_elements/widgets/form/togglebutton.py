# -*- coding: UTF-8 -*-

# togglebutton.py
# Created by Filippo Astolfi on 2010-10-13.
# Copyright (c) 2010 Softwell. All rights reserved.

"""Toggle buttons"""

class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerFull"
    # dojo_theme='claro'    # !! Uncomment this row for Dojo_1.5 usage
    
    def test_1_basic(self,pane):
        """Simple test"""
        pane.div('We show you here a simple togglebuttons set:',
                  font_size='.9em',text_align='justify')
        fb=pane.formbuilder(border_spacing='10px',datapath='test1')
        fb.togglebutton(value='^.toggle1',iconClass="dijitRadioIcon",label='label')
        fb.togglebutton(value='^.toggle2',iconClass="dijitRadioIcon",label='another label')
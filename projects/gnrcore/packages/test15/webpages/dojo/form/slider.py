# -*- coding: UTF-8 -*-

"""Slider"""

from gnr.core.gnrbag import Bag

class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerFull"
    dojo_theme = 'tundra'
    
    def test_1_basic(self, pane):
        """horizontalSlider"""
        fb = pane.formbuilder(cols=2, border_spacing='3px', width='100%', fld_width='30px')
        fb.horizontalSlider(value='^.number', lbl='Number', width='20em')

        

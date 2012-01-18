# -*- coding: UTF-8 -*-
"""dateTextbox"""

class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerFull"
    
    def test_1_basic(self, pane):
        """simple dateTextbox"""
        fb = pane.formbuilder()
        fb.dateTextbox(value='^.date', lbl='Date')
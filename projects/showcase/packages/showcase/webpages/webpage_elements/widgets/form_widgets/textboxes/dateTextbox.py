# -*- coding: UTF-8 -*-
"""dateTextbox"""

class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerFull"
    
    def test_1_dateTextbox(self, pane):
        """dateTextbox"""
        fb = pane.formbuilder(datapath='test1')
        fb.dateTextbox(value='^.dateTextbox', popup=True)
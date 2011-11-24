# -*- coding: UTF-8 -*-
"""currencyTextbox"""

class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerFull"
    
    def test_1_currencyTextbox(self, pane):
        """currencyTextbox"""
        fb = pane.formbuilder(datapath='test1')
        fb.currencyTextBox(value='^.amount', currency='EUR', locale='it')
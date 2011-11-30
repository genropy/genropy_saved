# -*- coding: UTF-8 -*-
"""Numberspinner"""

class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerFull"
    
    def test_1_numberSpinner(self, pane):
        """numberSpinner"""
        fb = pane.formbuilder()
        fb.data('.number',1)
        fb.div('Try to hold down a button: the spinning accelerates to make coarser adjustments easier.')
        fb.div('A lower limit of \'-10\' is set')
        fb.numberSpinner(value='^.number', min=-10, lbl='number')
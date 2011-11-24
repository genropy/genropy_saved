# -*- coding: UTF-8 -*-
"""Numberspinner"""

class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerFull"
    
    def test_1_numberSpinner(self, pane):
        """numberSpinner"""
        fb = pane.formbuilder(datapath='test1', cols=2)
        fb.data('.number',1)
        fb.numberSpinner(value='^.number', min=0, lbl='number')
        fb.div("""Try to hold down a button: the spinning accelerates
                    to make coarser adjustments easier""",
               font_size='.9em', text_align='justify', margin='5px')
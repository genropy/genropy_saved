# -*- coding: UTF-8 -*-
"""numberTextbox"""

class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerFull"
    
    def test_1_numberTextbox(self, pane):
        """numberTextbox"""
        fb = pane.formbuilder(datapath='test1', cols=2)
        fb.numberTextBox(value='^.numberTextbox')
        fb.div("""A simple number textbox. You can write any number with no more than three 
                decimals.""", font_size='.9em', text_align='justify')
        fb.numberTextbox(value='^.numberTextbox_2', places=3)
        fb.div("With \"places=3\" you must write a number with three decimals.",
               font_size='.9em', text_align='justify')
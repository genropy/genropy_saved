# -*- coding: UTF-8 -*-

# numberspinner.py
# Created by Filippo Astolfi on 2010-09-17.
# Copyright (c) 2010 Softwell. All rights reserved.

"""Numberspinner"""

class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerFull"
    # dojo_theme='claro'    # !! Uncomment this row for Dojo_1.5 usage

    def test_1_numberSpinner(self, pane):
        """numberSpinner"""
        fb = pane.formbuilder(datapath='test1', cols=2)
        fb.numberSpinner(value='^.number', default=100, min=0, lbl='number')
        fb.div("""Try to hold down a button: the spinning accelerates
                    to make coarser adjustments easier""",
               font_size='.9em', text_align='justify', margin='5px')

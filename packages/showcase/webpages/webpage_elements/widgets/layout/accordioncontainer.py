# -*- coding: UTF-8 -*-

# accordion.py
# Created by Filippo Astolfi on 2010-09-01.
# Copyright (c) 2010 Softwell. All rights reserved.

"""Accordion container"""

class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerFull"
    # dojo_theme='claro'    # !! Uncomment this row for Dojo_1.5 usage

    def test_1_basic(self, pane):
        """Basic accordion container"""
        pane.div("""In this example we will show you an example of an accordion container.""",
                 font_size='.9em', text_align='justify', margin_bottom='10px')
        ac = pane.accordionContainer(height='300px', selected='^selected')
        ap1 = ac.accordionPane(title='Pane one')
        ap1.div("""Click on the "Pane three"!""",
                font_size='.9em', text_align='justify', margin='10px')
        ap2 = ac.accordionPane(title='Pane two')
        ap3 = ac.accordionPane(title='Pane three')
        ap3.div("""The content of a pane will be showned when user chooses the corresponding pane.""",
                font_size='.9em', text_align='justify', margin='10px')

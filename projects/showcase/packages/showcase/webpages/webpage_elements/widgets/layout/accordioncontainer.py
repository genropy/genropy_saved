# -*- coding: UTF-8 -*-
"""Accordion container"""

class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerFull"
    
    def test_1_basic(self, pane):
        """Basic accordion container"""
        ac = pane.accordionContainer(height='300px', selected='^selected')
        ap1 = ac.accordionPane(title='Pane one')
        ap1.div("""Click on the "Pane three"!""",
                font_size='.9em', text_align='justify', margin='10px')
        ap2 = ac.accordionPane(title='Pane two')
        ap3 = ac.accordionPane(title='Pane three')
        ap3.div("""The content of a pane will be shown when user chooses the corresponding pane.""",
                font_size='.9em', text_align='justify', margin='10px')
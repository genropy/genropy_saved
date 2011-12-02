# -*- coding: UTF-8 -*-
"""timeTextbox"""

class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerFull"
    
    def test_1_timeTextbox(self, pane):
        """timeTextbox"""
        fb = pane.formbuilder()
        fb.timeTextBox(value='^.timeTextbox', lbl='Appointment')
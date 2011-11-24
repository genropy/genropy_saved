# -*- coding: UTF-8 -*-
"""Dojo toolbar"""

class GnrCustomWebPage(object):
    py_requires = """gnrcomponents/testhandler:TestHandlerFull"""
    
    def test_1_basic(self, pane):
        """Basic example"""
        tb = pane.toolbar(height='20px')
        fb = tb.formbuilder(cols=8, border_spacing=0)
        for i in ['icnBaseAdd', 'icnBuilding', 'icnBaseCalendar',
                  'icnBuddy', 'queryMenu', 'icnBuddyChat']:
            fb.slotButton('tooltip', iconClass=i, action='alert("Performing an action...")')
        fb.textbox()
        fb.button('save', action='alert("Saving!")')
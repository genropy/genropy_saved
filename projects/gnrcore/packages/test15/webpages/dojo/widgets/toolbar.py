# -*- coding: UTF-8 -*-

"""toolbar"""

class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerBase"
    
    def test_1_toolbar(self, pane):
        """basic"""
        tb = pane.toolbar(height='20px')
        fb = tb.formbuilder(cols=8, border_spacing=0)
        fb.slotButton('tooltip', iconClass="icnBaseAdd")
        fb.slotButton('tooltip', iconClass="icnBuilding")
        fb.slotButton('tooltip', iconClass="icnBaseCalendar")
        fb.slotButton('tooltip', iconClass="icnBuddy")
        fb.slotButton('tooltip', iconClass="queryMenu")
        fb.slotButton('tooltip', iconClass="icnBuddyChat")
        fb.textbox()
        fb.button('save', action='alert("Saving!")')
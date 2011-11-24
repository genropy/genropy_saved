# -*- coding: UTF-8 -*-
"""slotToolbar"""

import datetime

class GnrCustomWebPage(object):
    py_requires = """gnrcomponents/testhandler:TestHandlerFull"""
    workdate = datetime.datetime.now().date()
    
    def test_1_basic(self,pane):
        """Basic example"""
        pane.data('.date', self.workdate)
        top = pane.div().slotToolbar(slotbarCode='top_0',slots='dummy,*,foo,boo,goo')
        fb = top.dummy.formbuilder(lbl_width='3em', lbl_color='teal', fld_width='14em')
        fb.dateTextbox(lbl='Date', value='^.date')
        top.foo.slotButton('Save', iconClass='iconbox save', action="alert('Saved data')")
        top.boo.slotButton('Delete', iconClass='iconbox trash', action="alert('Deleted data')")
        top.goo.slotButton('New document', iconClass='iconbox document', action="alert('Starting new document...')")
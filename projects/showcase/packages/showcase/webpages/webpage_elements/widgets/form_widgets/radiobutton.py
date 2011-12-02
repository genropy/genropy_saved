# -*- coding: UTF-8 -*-
"""Radio buttons"""

class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerFull"
    
    def test_1_basic(self, pane):
        """Simple test"""
        fb = pane.formbuilder(datapath='.radio', cols=1)
        
        fb.div("""We show you here a simple radio buttons set.
                  The \"group\" attribute allows to create radiobuttons related each others.""")
        fb.div("""You can specify a default selection with \"default_value=True\"""")
        fb.radiobutton(value='^.jazz', group='genre1', label='Jazz')
        fb.radiobutton(value='^.rock', group='genre1', label='Rock')
        fb.radiobutton(value='^.blues', group='genre1', label='Blues', default_value=True)
        
        pane.div('Here we show you an other radio buttons set.', margin_left='12px')
        fb = pane.formbuilder(datapath='.sex', cols=3, lbl_width='3em', fld_width='4em')
        fb.div('Sex')
        fb.radiobutton(value='^.male', group='genre2', label='M')
        fb.radiobutton(value='^.female', group='genre2', label='F')
# -*- coding: UTF-8 -*-

"""slotButtons"""

class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerBase"
    
    def test_1_basic(self, pane):
        """Basic button"""
        pane.slotButton('I\'m a button', iconClass="icnBuilding", action='alert("Hello!")')
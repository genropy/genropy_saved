# -*- coding: UTF-8 -*-

"""Buttons"""

class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerBase"
    
    def test_1_basic(self, pane):
        """Basic button"""
        pane.timetextbox(value='^.ttb')
        pane.div('^.ttb')

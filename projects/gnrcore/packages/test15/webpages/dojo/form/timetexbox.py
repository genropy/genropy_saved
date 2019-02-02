# -*- coding: utf-8 -*-

"""Buttons"""

from builtins import object
class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerBase"
    
    def test_1_basic(self, pane):
        """Basic button"""
        pane.timetextbox(value='^.ttb')
        pane.div('^.ttb')

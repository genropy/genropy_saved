# -*- coding: UTF-8 -*-
"""HTML"""

class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerBase"
    
    def test_1_todo(self, pane):
        """TODO"""
        pane.div('TODO')
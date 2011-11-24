# -*- coding: UTF-8 -*-
"""Checkbox"""

class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerFull"
    
    def test_1_basic(self, pane):
        """Checkbox"""
        labels = 'First,Second,Third'
        labels = labels.split(',')
        pane = pane.formbuilder()
        for label in labels:
            pane.checkbox(value='^.%s_checkbox' % label, label=label)
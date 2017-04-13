# -*- coding: UTF-8 -*-

# tree.py
# Created by Filippo Astolfi on 2011-12-02.
# Copyright (c) 2011 Softwell. All rights reserved.

"""numberTextBox"""

from gnr.core.gnrdecorator import public_method
class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerBase"
    
    def windowTitle(self):
        return 'TextBox'
        

    def test_0_base(self, pane):
        fb = pane.formbuilder(cols=2,datapath='.data')
        fb.textBox(value='^.test',validate_regex=' ^[AB]*$')

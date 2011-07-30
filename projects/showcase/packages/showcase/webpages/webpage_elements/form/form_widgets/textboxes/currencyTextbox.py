# -*- coding: UTF-8 -*-

# currencyTextbox.py
# Created by Filippo Astolfi on 2010-09-08.
# Copyright (c) 2010 Softwell. All rights reserved.

"""currencyTextbox"""

class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerFull"
    
    def test_1_currencyTextbox(self, pane):
        """currencyTextbox"""
        fb = pane.formbuilder(datapath='test1')
        fb.currencyTextBox(value='^.amount', currency='EUR', locale='it')
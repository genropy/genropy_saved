# -*- coding: UTF-8 -*-

# dateTextbox.py
# Created by Filippo Astolfi on 2010-09-17.
# Copyright (c) 2010 Softwell. All rights reserved.

"""dateTextbox"""

class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerFull"
    
    def test_1_dateTextbox(self, pane):
        """dateTextbox"""
        fb = pane.formbuilder(datapath='test1')
        fb.dateTextbox(value='^.dateTextbox', popup=True)
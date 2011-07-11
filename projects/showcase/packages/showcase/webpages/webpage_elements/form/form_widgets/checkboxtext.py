# -*- coding: UTF-8 -*-

# checkboxtext.py
# Created by Filippo Astolfi on 2010-09-06.
# Copyright (c) 2010 Softwell. All rights reserved.

"""checkBoxText"""

class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerFull"

    def windowTitle(self):
        return 'Hello'
         
    def test_0_firsttest(self,pane):
        """checkboxtext"""
        pane.checkBoxText('foo,bar,span',value='^.pluto',separator=' - ')
        pane.textbox(value='^.pluto')
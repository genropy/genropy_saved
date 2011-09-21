# -*- coding: UTF-8 -*-

# checkboxgroup.py
# Created by Francesco Porcari on 2011-06-24.
# Copyright (c) 2011 Softwell. All rights reserved.

"Test page description"
class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerFull"

    def windowTitle(self):
        return ''
         
    def test_0_firsttest(self,pane):
        """First test description"""
        pane.checkBoxText('foo,bar,span',value='^.pluto',separator=' -     ')
        pane.textbox(value='^.pluto')
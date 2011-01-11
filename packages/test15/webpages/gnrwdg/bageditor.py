# -*- coding: UTF-8 -*-

# bagEditor.py
# Created by Francesco Porcari on 2011-01-10.
# Copyright (c) 2011 Softwell. All rights reserved.

"Test page description"
class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerFull"

    def windowTitle(self):
        return ''
         
    def test_0_firsttest(self,pane):
        """First test description"""
        pane.contentPane(height='400px',background='lime').bagEditor(bagpath='gnr',datapath='pippo')
        
# -*- coding: UTF-8 -*-

# bagNodeEditor.py
# Created by Francesco Porcari on 2011-01-10.
# Copyright (c) 2011 Softwell. All rights reserved.

"Test page description"
class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerFull"

    def windowTitle(self):
        return ''
         
    def test_0_firsttest(self,pane):
        """First test description"""
        bc = pane.borderContainer(height='400px',background='lime')
        bc.contentPane(region='top').button('load node',action='genro.publish("test_editnode","")')
        bc.contentPane(region='center').bagNodeEditor(bagpath='gnr',nodeId='test')
        
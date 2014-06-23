# -*- coding: UTF-8 -*-

# tpleditor.py
# Created by Francesco Porcari on 2011-10-20.
# Copyright (c) 2011 Softwell. All rights reserved.

"Test page description"
class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerFull,gnrcomponents/tpleditor:TemplateEditor"

    def windowTitle(self):
        return ''
         
    def test_0_firsttest(self,pane):
        """First test description"""
        bc = pane.borderContainer(height='600px')
        bc.contentPane(region='center').templateEditor(maintable='polimed.medico')
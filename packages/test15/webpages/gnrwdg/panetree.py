# -*- coding: UTF-8 -*-

# frametree.py
# Created by Francesco Porcari on 2011-01-21.
# Copyright (c) 2011 Softwell. All rights reserved.

"Test page description"
class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerFull"
    css_requires='csstest'

    def windowTitle(self):
        return ''
         
    def test_0_firsttest(self,pane):
        """First test description"""
        pane.div(height='6px',width='6px',background='red',_class='hiddenDock').palettePane('pippo',title='Pippo',dockTo='*')
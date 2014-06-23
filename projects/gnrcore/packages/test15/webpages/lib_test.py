# -*- coding: UTF-8 -*-

# panetree.py
# Created by Francesco Porcari on 2011-01-21.
# Copyright (c) 2011 Softwell. All rights reserved.

"panetree"
from gnrpkg.test15.test_test import pippo

class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerFull"
    css_requires='csstest'
    
    def windowTitle(self):
        return 'panetree'
         
    def test_0_hiddendock(self,pane):
        """hiddenDock"""
        pane.div(height='6px',width='6px',background='red',
                 _class='hiddenDock').palettePane('pippo',title='Pippo',dockTo='*')
        pippo()
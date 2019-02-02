# -*- coding: utf-8 -*-

# untitled.py
# Created by Francesco Porcari on 2011-05-13.
# Copyright (c) 2011 Softwell. All rights reserved.

"Test page description"
from builtins import object
class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerFull,th/th"

    def windowTitle(self):
        return ''
    
  # def test_0_iframe_autosize(self,pane):
  #     pane.iframe(src='/sys/thpage/glbl/provincia?th_public=false',autoSize=True)
    
         
    def test_0_palette(self,pane):
        """First test description"""
        pane.palettePane(paletteCode='pippo',title='pippo',dockButton=True,
                                height='4000px',
                                width='3000px').div('CIao')
        
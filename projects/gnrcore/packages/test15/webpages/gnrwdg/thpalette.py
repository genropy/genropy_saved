# -*- coding: UTF-8 -*-

# untitled.py
# Created by Francesco Porcari on 2011-05-13.
# Copyright (c) 2011 Softwell. All rights reserved.

"Test page description"
class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerFull,th/th"

    def windowTitle(self):
        return ''
    
  # def test_0_iframe_autosize(self,pane):
  #     pane.iframe(src='/sys/thpage/glbl/provincia?th_public=false',autoSize=True)
    
         
    def test_0_thpalette(self,pane):
        """First test description"""
        dialog = pane.thIframeDialog(table='glbl.provincia')
        pane.button('open',action='console.log(dialog)',dialog=dialog.js_widget)
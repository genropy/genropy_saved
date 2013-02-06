# -*- coding: UTF-8 -*-

# gnrlayout.py
# Created by Francesco Porcari on 2011-01-27.
# Copyright (c) 2011 Softwell. All rights reserved.

"gnrlayout"

class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerFull,gnrcomponents/graphiframe/graphiframe:GraphIframe"
    
    def windowTitle(self):
        return 'gnrlayout'
         
    def test_0_framePane(self,pane):
        """test 0"""
        frame = pane.framePane(frameCode='frame0',height='300px')
        top = frame.top.slotToolbar(slots='*,|,piero,|,*',_class='frame_footer')
        top.piero.div('piero')
        frame.graphIframe(x='pippo')

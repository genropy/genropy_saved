# -*- coding: UTF-8 -*-

# gnrlayout.py
# Created by Francesco Porcari on 2011-01-27.
# Copyright (c) 2011 Softwell. All rights reserved.

"Test page description"
class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerFull"

    def windowTitle(self):
        return ''
         
    def test_0_framePane(self,pane):
        """First test description"""
        frame = pane.framePane(height='300px')
        top = frame.slotFooter(slots='*,|,piero,|,*',_class='frame_footer')
        frame.div('HEI I AM CENTER')
        
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
        top = frame.top.slotToolbar(slots='*,piero,*',height='20px')
        top.piero.button('Run',fire='.run')
        iframe = frame.center.contentPane(overflow='hidden').graphIframe()
        frame.dataController("""
            gnrgraph.test(iframe,testh,testw);

            """,iframe=iframe,testh=100,testw=100,_fired='^.run')

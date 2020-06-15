# -*- coding: utf-8 -*-

# iframerunner.py
# Created by Francesco Porcari on 2011-04-19.
# Copyright (c) 2011 Softwell. All rights reserved.

"iframerunner"

from gnr.core.gnrdecorator import public_method
from gnr.core.gnrbag import Bag

class GnrCustomWebPage(object):
    py_requires="""gnrcomponents/testhandler:TestHandlerFull,
                    test_proxy:Leonard AS leo
                """
    

    def test_0_simple(self,pane):
        self.leo.makeBox(pane)
        self.leo.fakeLaugh()

    #def test_0_bazinga(self,pane):
    #    self.sheldon.printBazinga()
    #    self.sheldon.seatOnCouch()
    #    self.sheldon.callPenny()
    #    self.sheldon.fakeLaugh()
    #    self.sheldon.bazingaBox(pane)

    
    #def test_1_remote(self,pane):
    #    pane.button('Run',fire='.run')
    #    pane.div('^.result')
    #    pane.dataRpc('.result',self.sheldon.remoteBazinga,_fired='^.run')
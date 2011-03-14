# -*- coding: UTF-8 -*-

# dynamicform.py
# Created by Francesco Porcari on 2010-12-27.
# Copyright (c) 2010 Softwell. All rights reserved.

"Test page description"
from gnr.core.gnrbag import Bag

class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerFull,proxy_tester"

    def test_0_data(self, pane):
        pane.div(self.proxy_test.ciao())


    def test_1_data(self, pane):

        pane.div('^test')
        pane.dataRpc('^test','proxy_test.ciao',_onStart=True)
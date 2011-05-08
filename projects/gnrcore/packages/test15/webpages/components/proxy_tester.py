# -*- coding: UTF-8 -*-

# proxy_tester.py
# Created by Francesco Porcari on 2010-12-27.
# Copyright (c) 2010 Softwell. All rights reserved.

"""proxy_tester"""

class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerFull,proxy_tester"
    
    def test_0_data(self, pane):
        pane.div(self.proxy_test.ciao_test())
        
    def test_1_data(self, pane):
        pane.div('^test')
        pane.dataRpc('^test',self.proxy_test.ciao,_onStart=True)
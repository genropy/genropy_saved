# -*- coding: UTF-8 -*-

# untitled.py
# Created by Francesco Porcari on 2011-04-19.
# Copyright (c) 2011 Softwell. All rights reserved.

"Test page description"
from gnr.web.gnrwebpage import public_method

class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerFull"        

    def test_1_firsttest(self,pane):
        """First test description"""
        pane = pane.contentPane(height='200px')
        iframe = pane.iframe(main='pippo',main_foo=36)

    @public_method
    def pippo(self,root,foo=None,**kwargs):        
        root.div(foo)
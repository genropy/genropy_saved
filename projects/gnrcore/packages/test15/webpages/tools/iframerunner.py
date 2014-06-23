# -*- coding: UTF-8 -*-

# iframerunner.py
# Created by Francesco Porcari on 2011-04-19.
# Copyright (c) 2011 Softwell. All rights reserved.

"iframerunner"

from gnr.core.gnrdecorator import public_method

class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerFull"
    
    def test_1_firsttest(self,pane):
        """First test description"""
        pane = pane.contentPane(height='300px')
        iframe = pane.iframe(main='pippo',main_foo=36)
        
    @public_method
    def pippo(self,root,foo=None,**kwargs):
        root.div(foo)
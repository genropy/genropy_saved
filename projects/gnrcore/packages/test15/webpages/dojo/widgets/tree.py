# -*- coding: UTF-8 -*-

# tree.py
# Created by Francesco Porcari on 2010-08-18.
# Copyright (c) 2010 Softwell. All rights reserved.

"""tree"""

class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerBase"
    dojo_theme = 'claro'
    
    def windowTitle(self):
        return 'Tree'
        
    def test_1_simple(self, root, **kwargs):
        """simple"""
        pass
        
class ToFix(object):
    """
    1-tooltip inspector
    """
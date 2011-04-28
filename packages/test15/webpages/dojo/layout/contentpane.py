# -*- coding: UTF-8 -*-

# contentpane.py
# Created by Francesco Porcari on 2010-08-18.
# Copyright (c) 2010 Softwell. All rights reserved.

"""contentPane"""

class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerBase"
    
    def windowTitle(self):
        return 'contentPane'
        
    def test_(self, pane):
        pass
        
class ToFix(object):
    """
    """
    
class FixedToCheck(object):
    """
    1-When rebuilded there is a property to get children but
    not the removechild function.
    Fixed but it suggests that we could have problems in rebulding for many widgets
    as we use magic trick instead of testing specific widget type.
    """
    
class Fixed(object):
    """docstring for Fixed"""
        
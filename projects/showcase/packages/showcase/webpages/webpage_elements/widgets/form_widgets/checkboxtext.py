# -*- coding: UTF-8 -*-
"""checkBoxText"""

class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerFull"
    
    def test_1_basic(self,pane):
        """checkboxtext"""
        pane.checkBoxText('name,surname,address',value='^.foo',separator=' - ')
        pane.simpleTextarea(value='^.foo')
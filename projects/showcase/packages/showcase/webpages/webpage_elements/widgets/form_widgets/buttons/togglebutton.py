# -*- coding: UTF-8 -*-
"""Toggle buttons"""

class GnrCustomWebPage(object):
    py_requires = "gnrcomponents/testhandler:TestHandlerFull"
    
    def test_1_basic(self, pane):
        """Simple test"""        
        pane.togglebutton(value='^.toggle', iconClass="dijitRadioIcon", label='A togglebutton')
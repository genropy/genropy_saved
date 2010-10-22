# -*- coding: UTF-8 -*-

# timeTextbox.py
# Created by Filippo Astolfi on 2010-09-08.
# Copyright (c) 2010 Softwell. All rights reserved.

"""timeTextbox"""

class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerFull"
    # dojo_theme='claro'    # !! Uncomment this row for Dojo_1.5 usage
    
    # For an exhaustive documentation, please see http://docs.genropy.org/widgets/form/textboxes/timetextbox.html
    
    def test_1_timeTextbox(self,pane):
        """timeTextbox"""
        fb = pane.formbuilder(datapath='test1')
        fb.timeTextBox(value='^.timeTextbox')
        

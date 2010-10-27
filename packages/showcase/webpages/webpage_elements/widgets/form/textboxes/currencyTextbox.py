# -*- coding: UTF-8 -*-

# currencyTextbox.py
# Created by Filippo Astolfi on 2010-09-08.
# Copyright (c) 2010 Softwell. All rights reserved.

"""currencyTextbox"""

class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerFull"
    # dojo_theme='claro'    # !! Uncomment this row for Dojo_1.5 usage
    
    # For an exhaustive documentation, please see http://docs.genropy.org/widgets/form/textboxes/currencytextbox.html
    
    def test_1_currencyTextbox(self,pane):
        """currencyTextbox"""
        fb = pane.formbuilder(datapath='test1')
        fb.currencyTextBox(value='^.amount',default=1123.34,currency='EUR',locale='it')
        
# -*- coding: UTF-8 -*-

# checkbox.py
# Created by Filippo Astolfi on 2010-09-01.
# Copyright (c) 2010 Softwell. All rights reserved.

"""Checkbox"""

class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerFull"
    # dojo_theme='claro'    # !! Uncomment this row for Dojo_1.5 usage
    
    # For an exhaustive documentation, please see http://docs.genropy.org/widgets/form/checkbox.html
    
    def test_1_basic(self,pane):
        """Basic checkbox"""
        fb = pane.formbuilder(datapath='test1',cols=2)
        fb.checkbox(value='^.checkbox',lbl='Checkbox')
        
    def test_2_checkbox(self,pane):
        """Checkbox"""
        labels = 'First,Second,Third'
        labels=labels.split(',')
        pane=pane.formbuilder(datapath='test2')
        for label in labels:
            pane.checkbox(value='^.%s_checkbox'%label,label=label)
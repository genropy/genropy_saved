# -*- coding: UTF-8 -*-

# dataFormula.py
# Created by Filippo Astolfi on 2010-10-27.
# Copyright (c) 2010 Softwell. All rights reserved.

"""dataFormula"""

class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerFull"
    # dojo_theme='claro'    # !! Uncomment this row for Dojo_1.5 usage
    
    def test_1_basic(self,pane):
        """dataFormula"""
        fb = pane.formbuilder(cols=2,datapath='test1')
        fb.horizontalSlider(lbl='Base',value='^.base',width='200px',minimum=1,maximum=100)
        fb.numberTextBox(value='^.base',places=2)
        fb.horizontalSlider(lbl='Height',value='^.height',width='200px',minimum=1,maximum=100)
        fb.numberTextBox(value='^.height',places=2)
        fb.dataFormula('.area','base * height', base='^.base', height='^.height')
        fb.numberTextBox(lbl='!!Area',value='^.area',places=2,border='2px solid grey',padding='2px')
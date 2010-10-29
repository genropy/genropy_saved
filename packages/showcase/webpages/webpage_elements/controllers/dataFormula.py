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
        pane.div("""In this basic example we show you a simple case of dataFormula:
                  setting the \'base\' value and the \'height\' value allow the dataFormula in the
                  calculation of the area of a rectangle.""",
                  colspan=2,font_size='.9em',text_align='justify')
        fb = pane.formbuilder(cols=2,datapath='test1')
        fb.horizontalSlider(lbl='Base',value='^.base',width='200px',minimum=1,maximum=100)
        fb.numberTextBox(value='^.base',places=2)
        fb.horizontalSlider(lbl='Height',value='^.height',width='200px',minimum=1,maximum=100)
        fb.numberTextBox(value='^.height',places=2)
        fb.dataFormula('.area','base * height', base='^.base', height='^.height')
        fb.numberTextBox(lbl='!!Rectangle area',value='^.area',places=2,border='2px solid grey',padding='2px')
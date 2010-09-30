# -*- coding: UTF-8 -*-

# numberTextbox.py
# Created by Niso on 2010-09-17.
# Copyright (c) 2010 Softwell. All rights reserved.

"""numberTextbox"""

class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerFull"
    # dojo_theme='claro'    # !! Uncomment this row for Dojo_1.5 usage
    
    # For an exhaustive documentation, please see http://docs.genropy.org/widgets/form/textboxes/numbertextbox.html
    
    #   - Other forms, attributes and items:
    #       In this section we report forms/attributes that have been used in this example
    #       despite they didn't strictly belonging to boxes.
    #       We also suggest you the file (if it has been created!) where you can find
    #       some documentation about them.
    #
    #       ## name ##          --> ## file ##
    #       cols                --> formbuilder.py
    #       datapath            --> datapath.py
    #       formbuilder         --> formbuilder.py
    #       value               --> datapath.py
    
    def test_1_numberTextbox(self,pane):
        """numberTextbox"""
        fb = pane.formbuilder(datapath='test1',cols=2)
        fb.numberTextBox(value='^.numberTextbox')
        fb.div("""A simple number textbox. You can write any number with no more than three 
                decimals.""",font_size='.9em',text_align='justify')
        fb.numberTextbox(value='^.numberTextbox_2',places=3)
        fb.div("With \"places=3\" you must write a number with three decimals.",
                   font_size='.9em',text_align='justify')
        
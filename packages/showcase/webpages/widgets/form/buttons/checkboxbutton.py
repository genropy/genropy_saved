# -*- coding: UTF-8 -*-

# checkboxbutton.py
# Created by Niso on 2010-09-01.
# Copyright (c) 2010 Softwell. All rights reserved.

"""Checkboxbutton"""

class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerFull"
    # dojo_theme='claro'    # !! Uncomment this row for Dojo_1.5 usage
    
    """
    ================
     Checkboxbutton
    ================
    
    .. currentmodule:: widgets

    .. class:: checkbox buttons -  Genropy checkbox buttons
    
    ???TO DO!!!!
    """
        
        #   - Other forms and attributes:
        #       In this section we report forms/attributes that have been used in this example
        #       despite they didn't strictly belonging to button.
        #       We also suggest you the file (if it has been created!) where you can find
        #       some documentation about them.
        #
        #       ## name ##      --> ## file ##
        #       datapath        --> datapath.py
        #       formbuilder     --> formbuilder.py
        #       menu            --> menu.py
        #       menuline        --> menu.py
        #       numberTextbox   --> textbox.py
        #       textbox         --> textbox.py
        #       value           --> datapath.py





def test_1_checkbox(self,pane):
    """Checkbox button"""
    pane.div(""" Here we show you an example of checkbox button.""",
            font_size='.9em',text_align='justify')
    labels = 'First,Second,Third'
    labels=labels.split(',')
    pane=pane.formbuilder()
    for label in labels:
        pane.checkbox(value='^cb_%s'%label, label=label)
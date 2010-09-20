# -*- coding: UTF-8 -*-

# checkbox.py
# Created by Niso on 2010-09-01.
# Copyright (c) 2010 Softwell. All rights reserved.

"""Checkbox"""

class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerFull"
    # dojo_theme='claro'    # !! Uncomment this row for Dojo_1.5 usage
    
    """
    ==========
     Checkbox
    ==========

    .. currentmodule:: widgets

    .. class:: checkbox -  Genropy checkbox

    **Definition**: same definition of Dojo checkbox (version 1.5). To show it, click here_.

    .. _here: http://docs.dojocampus.org/dijit/form/CheckBox

    	Genro checkbox is the combination between an HTML checkbox and a Dojo checkbox.

    	Example::

    		pane.checkbox(value='^name',label='Name')
    """
        
        #   - Other forms and attributes:
        #       In this section we report forms/attributes that have been used in this example
        #       despite they didn't strictly belonging to button.
        #       We also suggest you the file (if it has been created!) where you can find
        #       some documentation about them.
        #
        #       ## name ##      --> ## file ##
        #       formbuilder     --> formbuilder.py
        
    def test_1_checkbox(self,pane):
        """Checkbox button"""
        pane.div(""" Here we show you an example of checkbox button.""",
                 font_size='.9em',text_align='justify')
        labels = 'First,Second,Third'
        labels=labels.split(',')
        pane=pane.formbuilder()
        for label in labels:
            pane.checkbox(value='^cb_%s'%label, label=label)
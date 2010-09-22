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

    .. currentmodule:: form

    .. class:: checkbox -  Genropy checkbox

    **Index:**

    	- Definition_

    	- Where_

    	- Description_

    	- Examples_

    	- Attributes_

    .. _Definition:

    **Definition**:

    	Same definition of Dojo checkbox (version 1.5). To show it, click here_.

    .. _here: http://docs.dojocampus.org/dijit/form/CheckBox

    .. _Where:

    **Where:**

    	#NISO ???

    .. _Description:

    **Description:**

    	Genro checkbox is the combination between an HTML checkbox and a Dojo checkbox; like in HTML and in Dojo, it is a widget that permits the user to make a selection between a boolean True/False choice.

    .. _Examples:

    **Examples**:

    	Example::

    		pane.checkbox(value='^name',label='Name')

    	Let's see its graphical result:

    	.. figure:: checkbox.png

    .. _Attributes:

    **Attributes**:

    	+--------------------+-------------------------------------------------+--------------------------+
    	|   Attribute        |          Description                            |   Default                |
    	+====================+=================================================+==========================+
    	| ``label``          | Set checkbox label                              |  ``None``                |
    	+--------------------+-------------------------------------------------+--------------------------+
    	| ``value``          | Set a path for checkbox value                   |  ``None``                |
    	+--------------------+-------------------------------------------------+--------------------------+
        
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
        #       lbl             --> formbuilder.py
        #       value           --> datapath.py
        
    def test_1_basic(self,pane):
        """Basic checkbox"""
        fb = pane.formbuilder(datapath='test1',cols=2)
        fb.checkbox(value='^.checkbox',lbl='Checkbox')
        fb.checkbox(value='^.checkbox2',lbl='Checkbox')
        
    def test_2_checkbox(self,pane):
        """Checkbox"""
        labels = 'First,Second,Third'
        labels=labels.split(',')
        pane=pane.formbuilder(datapath='test2')
        for label in labels:
            pane.checkbox(value='^.%s_checkbox'%label,label=label)
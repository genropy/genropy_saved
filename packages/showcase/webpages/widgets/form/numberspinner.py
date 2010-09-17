# -*- coding: UTF-8 -*-

# numberspinner.py
# Created by Niso on 2010-09-17.
# Copyright (c) 2010 Softwell. All rights reserved.

"""Numberspinner"""

class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerFull"
    # dojo_theme='claro'    # !! Uncomment this row for Dojo_1.5 usage
    
    """
    ===============
     numberspinner
    ===============

    .. currentmodule:: form

    .. class:: spinner -  Genropy spinner

        Numberspinner is similar to numberTextBox, but makes integer entry easier when
                         small adjustments are required.

						There are two features:

                         - The down and up arrow buttons "spin" the number up and down.
                         - Furthermore, when you hold down the buttons, the spinning accelerates to make coarser adjustments easier.    
        
    		+----------------+---------------------------------------------------------+-------------+
    		|   Attribute    |          Description                                    |   Default   |
    		+================+=========================================================+=============+
    		| ``font_size``  | CSS attribute                                           |  ``1em``    |
    		+----------------+---------------------------------------------------------+-------------+
    		| ``text_align`` | CSS attribute                                           |  ``left``   |
    		+----------------+---------------------------------------------------------+-------------+
    		| ``default``    | Add a default number to the spinner                     |  ``None``   |
    		+----------------+---------------------------------------------------------+-------------+
    		| ``min=NUMBER`` | set min value of numberSpinner                          |  ``None``   |
    		+----------------+---------------------------------------------------------+-------------+
    		| ``max=NUMBER`` | set max value of numberSpinner                          |  ``None``   |
    		+----------------+---------------------------------------------------------+-------------+

    		example::

    			pane.numberSpinner(value='^.age',default=100,min=0)
        """
        
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
    
    def test_1_numberSpinner(self,pane):
        """numberSpinner"""
        fb = pane.formbuilder(datapath='test1',cols=2)
        fb.numberSpinner(value='^.age',default=100,min=0)
        fb.div("""Try to hold down a button: the spinning accelerates
                    to make coarser adjustments easier""",
                   font_size='.9em',text_align='justify',margin='5px')
                   
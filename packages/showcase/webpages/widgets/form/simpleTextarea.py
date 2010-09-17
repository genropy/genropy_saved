# -*- coding: UTF-8 -*-

# simpleTextarea.py
# Created by Niso on 2010-09-17.
# Copyright (c) 2010 Softwell. All rights reserved.

"""simpleTextarea"""

class GnrCustomWebPage(object):
    py_requires="gnrcomponents/testhandler:TestHandlerFull"
    # dojo_theme='claro'    # !! Uncomment this row for Dojo_1.5 usage

    """
    ================
     simpleTextarea
    ================
    
    .. currentmodule:: form

    .. class:: simpleTextarea -  Genropy simpleTextarea
    
        A simple text area.
    
    +----------------+---------------------------------------------------------+-------------+
	|   Attribute    |          Description                                    |   Default   |
	+================+=========================================================+=============+
	| ``font_size``  | CSS attribute                                           |  ``1em``    |
	+----------------+---------------------------------------------------------+-------------+
	| ``text_align`` | CSS attribute                                           |  ``left``   |
	+----------------+---------------------------------------------------------+-------------+
	| ``default``    | Add a text to your area                                 |  ``None``   |
	+----------------+---------------------------------------------------------+-------------+

        example::

	        pane.simpleTextarea(value='^.simpleTextarea',height='80px',width='30em',
                                colspan=2,color='blue',font_size='1.2em',
                                default='A simple area to contain text.')
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
    
    def test_1_simpleTextarea(self,pane):
        """simpleTextarea"""
        fb = pane.formbuilder(datapath='test1')
        fb.simpleTextarea(value='^.simpleTextarea',height='80px',width='30em',
                            colspan=2,color='blue',font_size='1.2em',
                            default='A simple area to contain text.')
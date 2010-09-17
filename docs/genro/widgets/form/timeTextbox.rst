=============
 timeTextbox
=============

.. currentmodule:: form

.. class:: timeTextbox -  Genropy timeTextbox

    A timeTextbox it's a time input control that allow either typing time or choosing it from a picker widget.
    
    - sintax: HH:MM
    
	+-----------------------+---------------------------------------------------------+-------------+
	|   Attribute           |          Description                                    |   Default   |
	+=======================+=========================================================+=============+
	| ``font_size``         | CSS attribute                                           |  ``1em``    |
	+-----------------------+---------------------------------------------------------+-------------+
	| ``text_align``        | CSS attribute                                           |  ``left``   |
	+-----------------------+---------------------------------------------------------+-------------+

	    example::

		    pane.timeTextBox(value='^timeTextbox')
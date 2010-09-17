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
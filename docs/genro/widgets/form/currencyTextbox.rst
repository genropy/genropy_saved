=================
 currencyTextbox
=================

.. currentmodule:: form

.. class:: currencyTextbox -  Genropy currencyTextbox

    The currencyTextbox inherits all the attributes and behaviors of the numberTextbox widget but are specialized for input monetary values, much like the currency type in spreadsheet programs.
        
	+-----------------------+---------------------------------------------------------+-------------+
	|   Attribute           |          Description                                    |   Default   |
	+=======================+=========================================================+=============+
	| ``font_size``         | CSS attribute                                           |  ``1em``    |
	+-----------------------+---------------------------------------------------------+-------------+
	| ``text_align``        | CSS attribute                                           |  ``right``  |
	+-----------------------+---------------------------------------------------------+-------------+
	| ``default``           | Add the default box value (use a default type supported |  ``None``   |
	|                       | from your box!). It's not compatible with dateTextbox   |             |
	|                       | and timeTextbox                                         |             |
	+-----------------------+---------------------------------------------------------+-------------+
	| ``currency``          | specify used currency                                   |  ``EUR``    |
	+-----------------------+---------------------------------------------------------+-------------+
	| ``locale``            | specify currency format type                            |  ``it``     |
	+-----------------------+---------------------------------------------------------+-------------+

		Example::

			pane.currencyTextBox(value='^amount',default=1123.34,currency='EUR',locale='it')
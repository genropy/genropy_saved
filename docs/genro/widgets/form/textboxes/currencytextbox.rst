=================
 CurrencyTextbox
=================

.. currentmodule:: form

.. class:: currencyTextbox -  Genropy currencyTextbox

	- :ref:`main-definition`
	
	- :ref:`where-is-it-?`
	
	- :ref:`some-examples`
	
	- :ref:`main-attributes`
	
	- :ref:`common-attributes`
	
	.. _main-definition:

Definition
==========

    The currencyTextbox inherits all the attributes and behaviors of the numberTextbox widget but are specialized for input monetary values, much like the currency type in spreadsheet programs.

	.. _where-is-it-?:

Where
=====

	#NISO ???

	.. _some-examples:

Examples
========

	Example::

		pane.currencyTextBox(value='^amount',default=1123.34,currency='EUR',locale='it')
	
	Let's see its graphical result:

	.. figure:: ???.png

	.. _main-attributes:

Attributes
==========

	+-----------------------+---------------------------------------------------------+-------------+
	|   Attribute           |          Description                                    |   Default   |
	+=======================+=========================================================+=============+
	| ``currency``          | specify used currency                                   |  ``EUR``    |
	+-----------------------+---------------------------------------------------------+-------------+
	| ``default``           | Add a default number to your text box                   |  ``None``   |
	+-----------------------+---------------------------------------------------------+-------------+
	| ``font_size``         | CSS attribute                                           |  ``1em``    |
	+-----------------------+---------------------------------------------------------+-------------+
	| ``locale``            | specify currency format type                            |  ``it``     |
	+-----------------------+---------------------------------------------------------+-------------+
	| ``text_align``        | CSS attribute                                           |  ``right``  |
	+-----------------------+---------------------------------------------------------+-------------+

	.. _common-attributes:

Common attributes
=================

	For common attributes, see :doc:`textboxes`
	
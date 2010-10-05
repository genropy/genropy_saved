	.. _textboxes-currencytextbox:

=================
 CurrencyTextbox
=================

.. currentmodule:: form

.. class:: currencyTextbox -  Genropy currencyTextbox

	- :ref:`currencyTextbox-definition`
	
	- :ref:`currencyTextbox-where`
	
	- :ref:`currencyTextbox-examples`
	
	- :ref:`currencyTextbox-attributes`
	
	- :ref:`currencyTextbox-other-attributes`
	
	.. _currencyTextbox-definition:

Definition
==========

    The currencyTextbox inherits all the attributes and behaviors of the numberTextbox widget but are specialized for input monetary values, much like the currency type in spreadsheet programs.

	.. _currencyTextbox-where:

Where
=====

	#NISO ???

	.. _currencyTextbox-examples:

Examples
========

	Example::

		class GnrCustomWebPage(object):
			def main(self,root,**kwargs):
				root.currencyTextBox(value='^amount',default=1123.34,currency='EUR',locale='it')
	
	Let's see a demo:

	#NISO add online demo!

	.. _currencyTextbox-attributes:

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

	.. _currencyTextbox-other-attributes:

Common attributes
=================

	For common attributes, see :ref:`textboxes-attributes`
	
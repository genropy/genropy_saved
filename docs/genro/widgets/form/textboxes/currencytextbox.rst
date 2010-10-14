	.. _genro-currencytextbox:

=================
 CurrencyTextbox
=================

.. currentmodule:: form

.. class:: currencyTextbox -  Genropy currencyTextbox

	- :ref:`currencyTextbox-definition-description`

	- :ref:`currencyTextbox-examples`

	- :ref:`currencyTextbox-attributes`

	- :ref:`currencyTextbox-other-attributes`

	We recommend you to read :ref:`genro-textboxes` first.

	.. _currencyTextbox-definition-description:

Definition and Description
==========================

    The currencyTextbox inherits all the attributes and behaviors of the numberTextbox widget but are specialized for input monetary values, much like the currency type in spreadsheet programs.

	.. _currencyTextbox-examples:

Examples
========

	Example::

		class GnrCustomWebPage(object):
			def main(self,root,**kwargs):
				root.currencyTextBox(value='^amount',default=1123.34,
				                     currency='EUR',locale='it')
	
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
	
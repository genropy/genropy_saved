	.. _genro-currencytextbox:

=================
 currencyTextbox
=================

	- :ref:`currencyTextbox-definition-description`
	
	- :ref:`currencyTextbox_attributes`
	
	- :ref:`currencyTextbox-examples`

	.. note:: We recommend you to read :ref:`genro-textboxes` first.

	.. _currencyTextbox-definition-description:

Definition and Description
==========================

	.. method:: pane.currencyTextbox([**kwargs])

    The currencyTextbox inherits all the attributes and behaviors of the numberTextbox widget but are specialized for input monetary values, much like the currency type in spreadsheet programs.

.. _currencyTextbox_attributes:

Attributes
==========

	**currencyTextbox**:
	
	* ``currency``: specify used currency. Default value is ``EUR``
	* ``default``: Add a default number to your widget. Default value is ``None``
	* ``locale``: specify currency format type. Default value is ``it``

	**common attributes**:

		For common attributes, see :ref:`textboxes_attributes`

	.. _currencyTextbox-examples:

Examples
========

	Example::

		class GnrCustomWebPage(object):
			def main(self,root,**kwargs):
				root.currencyTextBox(value='^amount',default=1123.34,
				                     currency='EUR',locale='it')	
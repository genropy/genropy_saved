.. _genro_numbertextbox:

=============
numberTextbox
=============

	- :ref:`numberTextbox_def`
	
	- :ref:`numberTextbox_attributes`
	
	- :ref:`numberTextbox_examples`

	.. note:: We recommend you to read :ref:`genro-textboxes` first.

.. _numberTextbox_def:

Definition and Description
==========================

	.. method:: pane.numberTextbox([default=None[, places=3]])
	
	A simple number textbox.
	
.. _numberTextbox_attributes:

Attributes
==========
	
	**numberTextbox**:
	
	* *default*: Add a default number to your numberTextbox. Default value is ``None``
	* *places*: Numbers of decimals. If it's reached the following decimal to the last supported one, a tooltip error will warn user. Default value is ``3``
	
	**common attributes**:

		For common attributes, see :ref:`textboxes_attributes`

.. _numberTextbox_examples:

Examples
========

	Example::
	
		class GnrCustomWebPage(object):
			def main(self,root,**kwargs):
				root.numberTextbox(value='^numberTextbox',places=2)
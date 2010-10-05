	.. _textboxes-numbertextbox:

===============
 NumberTextbox
===============

.. currentmodule:: form

.. class:: numberTextbox -  Genropy numberTextbox

	- :ref:`numberTextbox-definition`
	
	- :ref:`numberTextbox-where`
	
	- :ref:`numberTextbox-examples`
	
	- :ref:`numberTextbox-attributes`
	
	- :ref:`numberTextbox-other-attributes`
	
	.. _numberTextbox-definition:

Definition
==========

	A simple number textbox.
	
	.. _numberTextbox-where:

Where
=====

	#NISO ???

	.. _numberTextbox-examples:

Examples
========

	Example::
	
		class GnrCustomWebPage(object):
			def main(self,root,**kwargs):
				root.numberTextbox(value='^numberTextbox',places=2)
	
	Let's see a demo:

	#NISO add online demo!

	.. _numberTextbox-attributes:

Attributes
==========
	
	+-----------------------+---------------------------------------------------------+-------------+
	|   Attribute           |          Description                                    |   Default   |
	+=======================+=========================================================+=============+
	| ``default``           | Add a default number to your text box                   |  ``None``   |
	+-----------------------+---------------------------------------------------------+-------------+
	| ``font_size``         | CSS attribute                                           |  ``1em``    |
	+-----------------------+---------------------------------------------------------+-------------+
	| ``text_align``        | CSS attribute                                           |  ``left``   |
	+-----------------------+---------------------------------------------------------+-------------+
	| ``places``            | Numbers of decimals. If it's reached the following      |  ``3``      |
	|                       | decimal to the last supported one, a tooltip error      |             |
	|                       | will warn user                                          |             |
	+-----------------------+---------------------------------------------------------+-------------+
	
	.. _numberTextbox-other-attributes:

Common attributes
=================

	For common attributes, see :ref:`textboxes-attributes`

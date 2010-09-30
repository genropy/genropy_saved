===============
 NumberTextbox
===============

.. currentmodule:: form

.. class:: numberTextbox -  Genropy numberTextbox

	- :ref:`main-definition`
	
	- :ref:`where-is-it-?`
	
	- :ref:`some-examples`
	
	- :ref:`main-attributes`
	
	- :ref:`common-attributes`
	
	.. _main-definition:

Definition
==========

	A simple number textbox.
	
	.. _where-is-it-?:

Where
=====

	#NISO ???

	.. _some-examples:

Examples
========

	Example::
	
		class GnrCustomWebPage(object):
			def main(self,root,**kwargs):
				root.numberTextbox(value='^numberTextbox',places=2)
	
	Let's see its graphical result:

	.. figure:: ???.png

	.. _main-attributes:

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

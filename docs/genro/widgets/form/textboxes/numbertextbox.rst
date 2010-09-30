===============
 NumberTextbox
===============

.. currentmodule:: form

.. class:: numberTextbox -  Genropy numberTextbox

	A simple number textbox.
	
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

		Example::

			pane.numberTextbox(value='^numberTextbox',places=2)
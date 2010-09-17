===============
 numberTextbox
===============

.. currentmodule:: form

.. class:: numberTextbox -  Genropy numberTextbox

	A simple number textbox.
	+-----------------------+----------------------------------------------------+-------------+
	|   Attribute           |          Description                               |   Default   |
	+=======================+====================================================+=============+
    | ``default``           | Add a default number to your textbox               |  ``None``   |
	+-----------------------+----------------------------------------------------+-------------+
	| ``font_size``         | CSS attribute                                      |  ``1em``    |
	+-----------------------+----------------------------------------------------+-------------+
	| ``text_align``        | CSS attribute                                      |  ``right``  |
	+-----------------------+----------------------------------------------------+-------------+
	| ``places``            | Numbers of decimals. If it's reached the following |  ``3``      |
	|                       | decimal to the last supported one, a tooltip error |             |
	|                       | will warn user                                     |             |
	+-----------------------+----------------------------------------------------+-------------+

		example::

			pane.numberTextbox(value='^numberTextbox',places=2)
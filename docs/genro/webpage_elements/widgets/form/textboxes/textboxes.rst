	.. _genro-textboxes:

==================================
 An Introduction to the Textboxes
==================================

	- :ref:`textboxes-introduction`

	- :ref:`textboxes-attributes`

	.. _textboxes-introduction:

Definition
==========

	Textbox is a form widget used to insert data.

	There are different textbox types:

	- :ref:`genro-textbox`

	- :ref:`genro-currencytextbox`

	- :ref:`genro-datetextbox`

	- :ref:`genro-numbertextbox`

	- :ref:`genro-timetextbox`

	The main feature of each of these textboxes is that Genro combines Dojo's textboxes with HTML's textboxes.

	.. _textboxes-attributes:

Common attributes
=================

	Here we show the attributes that belong to every textbox:

	+--------------------+-------------------------------------------------+--------------------------+
	|   Attribute        |          Description                            |   Default                |
	+====================+=================================================+==========================+
	| ``datapath``       | Set path for data.                              |  ``None``                |
	|                    | For more details, see :ref:`genro_datapath`     |                          |
	+--------------------+-------------------------------------------------+--------------------------+
	| ``disabled``       | If True, user can't act on the textbox.         |  ``False``               |
	|                    | For more details, see :ref:`genro-disabled`     |                          |
	+--------------------+-------------------------------------------------+--------------------------+
	| ``hidden``         | Hide the textbox.                               |  ``False``               |
	|                    | See :ref:`genro-hidden`                         |                          |
	+--------------------+-------------------------------------------------+--------------------------+
	| ``value``          | Set a path for textbox's value.                 |  ``None``                |
	|                    | For more details, see :ref:`genro_datapath`     |                          |
	+--------------------+-------------------------------------------------+--------------------------+

	.. _textboxes-textboxes:

===========
 Textboxes
===========

.. currentmodule:: form

.. class:: textbox -  Genropy textbox

Definition
==========

	Textbox is a form widget used to insert data.

	There are different textbox types:

	- :ref:`textboxes-textbox`

	- :ref:`textboxes-currencytextbox`

	- :ref:`textboxes-datetextbox`

	- :ref:`textboxes-numbertextbox`

	- :ref:`textboxes-timetextbox`

	The main feature of each of these textboxes is that Genro combines Dojo's textboxes with HTML's textboxes.

	.. _textboxes-attributes:

Common attributes
=================

	Here we show the attributes that belong to every textbox:

	+--------------------+-------------------------------------------------+--------------------------+
	|   Attribute        |          Description                            |   Default                |
	+====================+=================================================+==========================+
	| ``datapath``       | Set path for data.                              |  ``None``                |
	|                    | For more details, see :ref:`common-datapath`    |                          |
	+--------------------+-------------------------------------------------+--------------------------+
	| ``disabled``       | If True, user can't act on the textbox.         |  ``False``               |
	|                    | For more details, see :ref:`common-disabled`    |                          |
	+--------------------+-------------------------------------------------+--------------------------+
	| ``hidden``         | Hide the textbox.                               |  ``False``               |
	|                    | See :ref:`common-hidden`                        |                          |
	+--------------------+-------------------------------------------------+--------------------------+
	| ``value``          | Set a path for textbox's value.                 |  ``None``                |
	|                    | For more details, see :ref:`common-datapath`    |                          |
	+--------------------+-------------------------------------------------+--------------------------+

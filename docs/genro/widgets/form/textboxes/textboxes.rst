===========
 Textboxes
===========

.. currentmodule:: form

.. class:: textbox -  Genropy textbox

	- :ref:`main-definition`

	- :ref:`where-is-it-?`

	- :ref:`A-brief-description`

	- :ref:`common-attributes`

	.. _main-definition:

Definition
==========

	Textbox is a form widget used to insert data.
	
	.. _where-is-it-?:

Where
=====

	#NISO ???
	
	.. _A-brief-description:

Description
===========

	There are different textbox types:
	
	- textbox
	
	- currencyTextbox
	
	- dateTextbox
	
	- numberTextbox
	
	- timeTextbox

	.. _common-attributes:

Common attributes
=================

	There are some common attributes to every textbox:

	+--------------------+-------------------------------------------------+--------------------------+
	|   Attribute        |          Description                            |   Default                |
	+====================+=================================================+==========================+
	| ``datapath``       | Set path for data.                              |  ``None``                |
	|                    | For more details, see :doc:`/common/datapath`   |                          |
	+--------------------+-------------------------------------------------+--------------------------+
	| ``disabled``       | If True, user can't act on the textbox.         |  ``False``               |
	|                    | For more details, see :doc:`/common/disabled`   |                          |
	+--------------------+-------------------------------------------------+--------------------------+
	| ``hidden``         | Hide the textbox.                               |  ``False``               |
	|                    | See :doc:`/common/hidden`                       |                          |
	+--------------------+-------------------------------------------------+--------------------------+
	| ``value``          | Set a path for textbox's value.                 |  ``None``                |
	|                    | For more details, see :doc:`/common/datastore`  |                          |
	+--------------------+-------------------------------------------------+--------------------------+

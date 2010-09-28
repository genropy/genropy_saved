==========
 Checkbox
==========

.. currentmodule:: form

.. class:: checkbox -  Genropy checkbox

Index
*****

	- :ref:`main-definition`
	
	- :ref:`where-is-it-?`
	
	- :ref:`A-brief-description`
	
	- :ref:`some-examples`
	
	- :ref:`main-attributes`
	
	.. _main-definition:

Definition
==========

	Same definition of Dojo checkbox (version 1.5). To show it, click here_.

	.. _here: http://docs.dojocampus.org/dijit/form/CheckBox

	.. _where-is-it-?:

Where
=====

	#NISO ???

	.. _A-brief-description:

Description
===========
	
	Genro checkbox is the combination between an HTML checkbox and a Dojo checkbox; like in HTML and in Dojo, it is a widget that permits the user to make a selection between a boolean True/False choice.

	.. _some-examples:

Examples
========

	Example::

		pane.checkbox(value='^name',label='Name')
		
	Let's see its graphical result:

	.. figure:: checkbox.png

	.. _main-attributes:

Attributes
==========

	+--------------------+-------------------------------------------------+--------------------------+
	|   Attribute        |          Description                            |   Default                |
	+====================+=================================================+==========================+
	| ``label``          | Set checkbox label                              |  ``None``                |
	+--------------------+-------------------------------------------------+--------------------------+
	| ``value``          | Set a path for checkbox value                   |  ``None``                |
	+--------------------+-------------------------------------------------+--------------------------+


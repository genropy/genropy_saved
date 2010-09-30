==========
 Checkbox
==========

.. currentmodule:: form

.. class:: checkbox -  Genropy checkbox

	- :ref:`checkbox-definition`
	
	- :ref:`checkbox-where`
	
	- :ref:`checkbox-description`
	
	- :ref:`checkbox-examples`
	
	- :ref:`checkbox-attributes`
	
	.. _checkbox-definition:

Definition
==========

	Same definition of Dojo checkbox (version 1.5). To show it, click here_.

	.. _here: http://docs.dojocampus.org/dijit/form/CheckBox

	.. _checkbox-where:

Where
=====

	#NISO ???

	.. _checkbox-description:

Description
===========
	
	Genro checkbox is the combination between an HTML checkbox and a Dojo checkbox; like in HTML and in Dojo, it is a widget that permits the user to make a selection between a boolean True/False choice.

	.. _checkbox-examples:

Examples
========

	Example::

		pane.checkbox(value='^name',label='Name')
		
	Let's see its graphical result:

	.. figure:: checkbox.png

	.. _`checkbox-attributes`:
	
Common attributes
=================

	+--------------------+-------------------------------------------------+--------------------------+
	|   Attribute        |          Description                            |   Default                |
	+====================+=================================================+==========================+
	| ``label``          | Set checkbox label                              |  ``None``                |
	+--------------------+-------------------------------------------------+--------------------------+
	| ``value``          | Set a path for checkbox value                   |  ``None``                |
	+--------------------+-------------------------------------------------+--------------------------+


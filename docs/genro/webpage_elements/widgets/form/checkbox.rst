	.. _genro-checkbox:

==========
 checkbox
==========

	- :ref:`checkbox-definition-description`

	- :ref:`checkbox-examples`
	
	- :ref:`checkbox-attributes`
	
	.. _checkbox-definition-description:

Definition and Description
==========================

	Same definition of Dojo checkbox (version 1.5). To show it, click here_.

	.. _here: http://docs.dojocampus.org/dijit/form/CheckBox

	Genro checkbox is the combination between an HTML checkbox and a Dojo checkbox; like in HTML and in Dojo, it is a widget that permits the user to make a selection between a boolean True/False choice.

	.. _checkbox-examples:

Examples
========

	Example::

		pane.checkbox(value='^name',label='Name')
		
	Let's see a demo:

	#NISO add online demo!

	.. _`checkbox-attributes`:
	
Common attributes
=================

	+--------------------+-------------------------------------------------+--------------------------+
	|   Attribute        |          Description                            |   Default                |
	+====================+=================================================+==========================+
	| ``disabled``       | If True, user can't act on the object.          |  ``False``               |
	|                    | For more details, see :ref:`genro-disabled`     |                          |
	+--------------------+-------------------------------------------------+--------------------------+
	| ``hidden``         | Hide the checkbox.                              |  ``False``               |
	|                    | See :ref:`genro-hidden`                         |                          |
	+--------------------+-------------------------------------------------+--------------------------+
	| ``label``          | Set checkbox label                              |  ``None``                |
	+--------------------+-------------------------------------------------+--------------------------+
	| ``value``          | Set a path for checkbox value                   |  ``None``                |
	+--------------------+-------------------------------------------------+--------------------------+


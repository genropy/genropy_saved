================
 SimpleTextarea
================

.. currentmodule:: form

.. class:: simpleTextarea -  Genropy simpleTextarea

	- :ref:`main-definition`
	
	- :ref:`where-is-it-?`
	
	- :ref:`A-brief-description`
	
	- :ref:`some-examples`
	
	- :ref:`main-attributes`
	
	- :ref:`common-attributes`

	.. _main-definition:

Definition
==========
		
	A simple text area.

	.. _where-is-it-?:

Where
=====

	#NISO ???

	.. _A-brief-description:

Description
===========

	???

	.. _some-examples:

Examples
========

	Let's see a code example::
	
		class GnrCustomWebPage(object):
			def main(self,root,**kwargs):
				root.simpleTextarea(value='^.simpleTextarea',height='80px',width='30em',
		                            colspan=2,color='blue',font_size='1.2em',
		                            default='A simple area to contain text.')

	Let's see its graphical result:

	.. figure:: ???.png

	.. _main-attributes:

Attributes
==========
	
	+--------------------+-------------------------------------------------+--------------------------+
	|   Attribute        |          Description                            |   Default                |
	+====================+=================================================+==========================+
	| ``font_size``      | CSS attribute                                   |  ``1em``                 |
	+--------------------+-------------------------------------------------+--------------------------+
	| ``text_align``     | CSS attribute                                   |  ``left``                |
	+--------------------+-------------------------------------------------+--------------------------+

	.. _common-attributes:

Common attributes
=================

	``default``: Add a text to your area. See :doc:`default`
	
	``disabled``: If True, user can't act on the simpletextarea. See :doc:`disabled`
	
	``hidden``: Hide the simpletextarea. See :doc:`hidden`
	
	``value``: Set a path for simpletextarea's text. See :doc:`value`
	
	
	
	+--------------------+-------------------------------------------------+--------------------------+
	|   Attribute        |          Description                            |   Default                |
	+====================+=================================================+==========================+
	| ``default``        | Add a text to your area                         |  ``None``                |
	+--------------------+-------------------------------------------------+--------------------------+
	| ``disabled``       | If True, user can't act on the simpletextarea.  |  ``False``               |
	|                    | For more details, see :doc:`/common/disabled`   |                          |
	+--------------------+-------------------------------------------------+--------------------------+
	| ``hidden``         | Hide the simpletextarea.                        |  ``False``               |
	|                    | See :doc:`/common/hidden`                       |                          |
	+--------------------+-------------------------------------------------+--------------------------+
	| ``value``          | Set a path for ???'s values.                    |  ``None``                |
	|                    | For more details, see :doc:`/common/datastore`  |                          |
	+--------------------+-------------------------------------------------+--------------------------+
	
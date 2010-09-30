================
 Simpletextarea
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

	+--------------------+-------------------------------------------------+--------------------------+
	|   Attribute        |          Description                            |   Default                |
	+====================+=================================================+==========================+
	| ``default``        | Add a text to the area.                         |  ``None``                |
	|                    | For more details, see :doc:`/common/disabled`   |                          |
	+--------------------+-------------------------------------------------+--------------------------+
	| ``disabled``       | If True, user can't act on the area.            |  ``False``               |
	|                    | For more details, see :doc:`/common/disabled`   |                          |
	+--------------------+-------------------------------------------------+--------------------------+
	| ``hidden``         | Hide the simpletextarea.                        |  ``False``               |
	|                    | See :doc:`/common/hidden`                       |                          |
	+--------------------+-------------------------------------------------+--------------------------+
	| ``value``          | Set a path for simpletextarea's value.          |  ``None``                |
	|                    | For more details, see :doc:`/common/datastore`  |                          |
	+--------------------+-------------------------------------------------+--------------------------+
	